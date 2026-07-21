import csv
import io
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID, uuid5, NAMESPACE_DNS
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.maintenance import Maintenance
from app.models.user import User
from app.schemas.technician_workload import TechnicianSummaryResponse, TechnicianDetail, TaskSummaryResponse, TaskDetail, TaskAssignRequest
from app.services.activity_service import activity_service, ActivityCreate
from app.services.notification_service import NotificationService
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum


class TechnicianWorkloadService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # TECHNICIAN MANAGEMENT
    # ---------------------------------------------------------
    
    def _generate_technician_profile(self, tech_name: str, tasks: List[Maintenance]) -> TechnicianDetail:
        """Dynamically generate a technician profile from maintenance tasks."""
        # Use a stable UUID based on the technician's name
        tech_id = uuid5(NAMESPACE_DNS, f"technician.{tech_name.lower()}")
        
        # Calculate workload
        assigned_jobs = len(tasks)
        active_jobs = sum(1 for t in tasks if t.status in ['Pending', 'Approved', 'In Progress'])
        assigned_vehicles = len(set(t.vehicle_id for t in tasks))
        
        # Determine status
        if active_jobs == 0:
            status = "Available"
        elif active_jobs >= 5:
            status = "Busy"
        else:
            status = "Assigned"
            
        # Hardcoded skills based on string hash for consistency
        all_skills = [
            "Engine Repair", "Tire Replacement", "Oil Change", 
            "Brake Service", "AC Service", "Body Repair", "Electrical"
        ]
        hash_val = hash(tech_name) % 100
        num_skills = (hash_val % 3) + 2
        skills = []
        for i in range(num_skills):
            skills.append(all_skills[(hash_val + i) % len(all_skills)])
            
        experience_levels = ["Junior", "Intermediate", "Senior", "Master"]
        exp = experience_levels[hash_val % len(experience_levels)]
        
        # Current capacity capped at 5
        max_capacity = 5
        utilization = min((active_jobs / max_capacity) * 100, 100)
        
        return TechnicianDetail(
            id=tech_id,
            name=tech_name,
            assigned_vehicles=assigned_vehicles,
            assigned_jobs=assigned_jobs,
            current_workload=active_jobs,
            utilization_pct=utilization,
            status=status,
            skills=list(set(skills)),
            experience_level=exp
        )

    def get_all_technicians(self, search: Optional[str] = None, status: Optional[str] = None) -> List[TechnicianDetail]:
        """Get all technicians derived from maintenance tasks."""
        # Get all maintenance records with a technician assigned
        records = self.db.query(Maintenance).filter(Maintenance.assigned_technician.isnot(None)).all()
        
        # Group by technician
        tech_tasks = {}
        for r in records:
            if r.assigned_technician not in tech_tasks:
                tech_tasks[r.assigned_technician] = []
            tech_tasks[r.assigned_technician].append(r)
            
        profiles = []
        for name, tasks in tech_tasks.items():
            profile = self._generate_technician_profile(name, tasks)
            profiles.append(profile)
            
        # Apply filters
        if status:
            profiles = [p for p in profiles if p.status.lower() == status.lower()]
            
        if search:
            search_lower = search.lower()
            profiles = [p for p in profiles if search_lower in p.name.lower() or str(p.id).startswith(search_lower)]
            
        return profiles

    def get_technician_summary(self) -> TechnicianSummaryResponse:
        profiles = self.get_all_technicians()
        total = len(profiles)
        active = sum(1 for p in profiles if p.status in ["Available", "Assigned", "Busy"])
        available = sum(1 for p in profiles if p.status == "Available")
        assigned = sum(1 for p in profiles if p.status == "Assigned")
        overloaded = sum(1 for p in profiles if p.current_workload > 5 or p.status == "Busy")
        
        avg_utilization = sum(p.utilization_pct for p in profiles) / total if total > 0 else 0
        
        return TechnicianSummaryResponse(
            total_technicians=total,
            active_technicians=active,
            available_technicians=available,
            assigned_technicians=assigned,
            overloaded_technicians=overloaded,
            technician_utilization_pct=avg_utilization
        )

    def export_technicians_csv(self, profiles: List[TechnicianDetail]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Name", "Assigned Vehicles", "Assigned Jobs", "Workload", "Utilization %", "Status", "Skills", "Experience"])
        for p in profiles:
            writer.writerow([
                str(p.id), p.name, p.assigned_vehicles, p.assigned_jobs, 
                p.current_workload, p.utilization_pct, p.status, 
                ", ".join(p.skills), p.experience_level
            ])
        return output.getvalue()
        
    def export_technicians_pdf(self, profiles: List[TechnicianDetail]) -> bytes:
        lines = ["TRANSITOPS - TECHNICIAN WORKLOAD EXPORT", "="*50, ""]
        for p in profiles:
            lines.append(f"Name: {p.name} (ID: {p.id})")
            lines.append(f"Status: {p.status} | Utilization: {p.utilization_pct}%")
            lines.append(f"Workload: {p.current_workload} active jobs")
            lines.append(f"Skills: {', '.join(p.skills)} ({p.experience_level})")
            lines.append("-" * 30)
        return "\n".join(lines).encode('utf-8')

    # ---------------------------------------------------------
    # MAINTENANCE TASKS
    # ---------------------------------------------------------
    
    def _map_to_task_detail(self, m: Maintenance) -> TaskDetail:
        return TaskDetail(
            task_id=m.id,
            vehicle_id=m.vehicle_id,
            vehicle_name=m.vehicle.vehicle_name if m.vehicle else "Unknown",
            vehicle_number=m.vehicle.registration_number if m.vehicle else "Unknown",
            maintenance_type=m.maintenance_type,
            assigned_technician=m.assigned_technician,
            priority=m.priority,
            status=m.status,
            scheduled_date=m.scheduled_date,
            estimated_duration=m.estimated_duration,
            completion_date=m.completed_date,
            created_at=m.created_at,
            updated_at=m.updated_at
        )

    def get_all_tasks(
        self, current_user: User, search: Optional[str] = None, status: Optional[str] = None, tech_name: Optional[str] = None
    ) -> List[TaskDetail]:
        query = self.db.query(Maintenance)
        
        # RBAC for technicians
        role_name = current_user.role.name if current_user.role else ""
        if role_name.lower() == "technician":
            query = query.filter(Maintenance.assigned_technician == current_user.full_name)
            
        if status:
            query = query.filter(Maintenance.status == status)
            
        if tech_name:
            query = query.filter(Maintenance.assigned_technician == tech_name)
            
        records = query.all()
        tasks = [self._map_to_task_detail(m) for m in records]
        
        if search:
            search_lower = search.lower()
            tasks = [t for t in tasks if 
                (t.assigned_technician and search_lower in t.assigned_technician.lower()) or 
                search_lower in str(t.task_id) or 
                search_lower in t.vehicle_name.lower() or 
                search_lower in t.vehicle_number.lower()
            ]
            
        return tasks

    def get_task_summary(self, current_user: User) -> TaskSummaryResponse:
        tasks = self.get_all_tasks(current_user=current_user)
        total = len(tasks)
        pending = sum(1 for t in tasks if t.status == "Pending")
        scheduled = sum(1 for t in tasks if t.status == "Approved") # Approved maps to Scheduled in this context
        in_progress = sum(1 for t in tasks if t.status == "In Progress")
        completed = sum(1 for t in tasks if t.status == "Completed")
        
        # Overdue: Scheduled date is past today and not completed
        today = date.today()
        overdue = sum(1 for t in tasks if t.status not in ["Completed", "Rejected"] and t.scheduled_date < today)
        
        return TaskSummaryResponse(
            total_tasks=total,
            pending_tasks=pending,
            scheduled_tasks=scheduled,
            in_progress_tasks=in_progress,
            completed_tasks=completed,
            overdue_tasks=overdue
        )

    def assign_technician(self, task_id: UUID, req: TaskAssignRequest, current_user: User) -> TaskDetail:
        m = self.db.query(Maintenance).filter(Maintenance.id == task_id).first()
        if not m:
            raise ValueError("Task not found")
            
        m.assigned_technician = req.technician_name
        self.db.commit()
        
        # Activity Log
        activity_service.log_activity(
            self.db,
            ActivityCreate(
                module=ModuleEnum.MAINTENANCE,
                activity_type=ActivityTypeEnum.UPDATED,
                title="Technician Assigned",
                description=f"Task {m.maintenance_number} assigned to {req.technician_name}",
                user_id=current_user.id,
                severity=SeverityEnum.INFO
            )
        )
        
        # Check if overloaded (mock logic)
        tasks = self.db.query(Maintenance).filter(Maintenance.assigned_technician == req.technician_name, Maintenance.status.in_(['Pending', 'Approved', 'In Progress'])).all()
        if len(tasks) > 5:
            NotificationService.notify_user(
                db=self.db,
                user_id=current_user.id,
                title="Technician Overloaded",
                description=f"Technician {req.technician_name} has exceeded capacity.",
                type="Alert",
                priority="High",
                category="System",
                module_name="Maintenance",
                severity="Warning"
            )
        else:
            NotificationService.notify_user(
                db=self.db,
                user_id=current_user.id,
                title="Task Assigned",
                description=f"Task {m.maintenance_number} assigned to {req.technician_name}.",
                type="Information",
                priority="Medium",
                category="System",
                module_name="Maintenance",
                severity="Info"
            )
            
        return self._map_to_task_detail(m)

    def export_tasks_csv(self, tasks: List[TaskDetail]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Task ID", "Vehicle Name", "Type", "Technician", "Priority", "Status", "Scheduled Date"])
        for t in tasks:
            writer.writerow([
                str(t.task_id), t.vehicle_name, t.maintenance_type, 
                t.assigned_technician or "Unassigned", t.priority, 
                t.status, t.scheduled_date.isoformat()
            ])
        return output.getvalue()
        
    def export_tasks_pdf(self, tasks: List[TaskDetail]) -> bytes:
        lines = ["TRANSITOPS - MAINTENANCE TASKS EXPORT", "="*50, ""]
        for t in tasks:
            lines.append(f"Task ID: {t.task_id} | Vehicle: {t.vehicle_name}")
            lines.append(f"Status: {t.status} | Priority: {t.priority}")
            lines.append(f"Technician: {t.assigned_technician}")
            lines.append("-" * 30)
        return "\n".join(lines).encode('utf-8')
