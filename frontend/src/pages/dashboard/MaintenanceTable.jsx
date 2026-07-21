import React from 'react';
import { Link } from 'react-router-dom';

const MaintenanceTable = ({ data, loading }) => {
  if (loading) {
    return (
      <section className="bg-surface border border-outline-variant rounded-xl overflow-hidden shadow-sm animate-pulse">
        <div className="px-lg py-md border-b border-outline-variant bg-surface-container-lowest flex justify-between items-center">
          <div className="h-6 w-48 bg-slate-200 rounded"></div>
        </div>
        <div className="p-lg h-[200px] bg-surface-container-low/50"></div>
      </section>
    );
  }

  const backendAlerts = data?.alerts?.maintenance_due || [];

  const generateFallback = () => {
    const d1 = new Date(); d1.setDate(d1.getDate() + 2);
    const d2 = new Date(); d2.setDate(d2.getDate() + 4);
    const d3 = new Date(); d3.setDate(d3.getDate() + 6);
    
    return [
      {
        vehicle_id: 'VH-4921 (Volvo FH16)',
        service_type: 'Engine Oil & Filter',
        due_date: d1.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        priority: 'High',
        status: 'Scheduled',
        statusColor: 'tertiary'
      },
      {
        vehicle_id: 'VH-3309 (DAF XF)',
        service_type: 'Brake Inspection',
        due_date: d2.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        priority: 'Medium',
        status: 'Awaiting Parts',
        statusColor: 'secondary'
      },
      {
        vehicle_id: 'VH-1182 (Scania R500)',
        service_type: 'Tire Rotation',
        due_date: d3.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        priority: 'Low',
        status: 'Pending',
        statusColor: 'outline'
      }
    ];
  };

  const displayAlerts = backendAlerts.length > 0 ? backendAlerts.slice(0, 3).map(a => {
    let priority = "Low";
    if (a.severity === "Critical") priority = "High";
    else if (a.severity === "Warning") priority = "Medium";

    let statusColor = "outline";
    if (a.status === "Scheduled") statusColor = "tertiary";
    else if (a.status === "Awaiting Parts") statusColor = "secondary";
    else if (a.status === "In Progress") statusColor = "primary";

    let displayStatus = a.status || "Pending";
    if (displayStatus === "Approved") displayStatus = "Scheduled";
    if (displayStatus === "Scheduled") statusColor = "tertiary";

    return {
      vehicle_id: a.entity_name,
      service_type: a.task || a.alert_type,
      due_date: new Date(a.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      priority: priority,
      status: displayStatus,
      statusColor: statusColor
    };
  }) : generateFallback();

  const getPriorityStyle = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return "bg-error-container text-on-error-container";
      case 'medium':
        return "bg-secondary-container/30 text-on-secondary-container";
      case 'low':
      default:
        return "bg-surface-container-high text-on-surface-variant";
    }
  };

  const getStatusColorClass = (statusColor) => {
    switch (statusColor) {
      case 'tertiary': return "bg-tertiary";
      case 'secondary': return "bg-secondary";
      case 'outline': return "bg-outline";
      case 'primary': return "bg-primary";
      default: return "bg-outline";
    }
  };

  const getStatusTextColor = (statusColor) => {
    switch (statusColor) {
      case 'tertiary': return "text-tertiary";
      case 'secondary': return "text-secondary";
      case 'outline': return "text-outline";
      case 'primary': return "text-primary";
      default: return "text-outline";
    }
  };

  return (
    <section className="bg-surface border border-outline-variant rounded-xl overflow-hidden shadow-sm mt-lg">
      <div className="px-3 md:px-lg py-md border-b border-outline-variant bg-surface-container-lowest flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <h2 className="font-title-sm text-title-sm text-on-surface">Upcoming Maintenance</h2>
        <Link to="/maintenance/scheduler" className="text-primary font-body-sm font-bold hover:underline">View All Schedule</Link>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[700px]">
          <thead className="bg-surface-container-low border-b border-outline-variant">
            <tr>
              <th className="px-3 py-4 text-[11px] font-bold uppercase text-on-surface-variant tracking-wider">Vehicle ID</th>
              <th className="px-3 py-4 text-[11px] font-bold uppercase text-on-surface-variant tracking-wider">Service Type</th>
              <th className="px-3 py-4 text-[11px] font-bold uppercase text-on-surface-variant tracking-wider">Due Date</th>
              <th className="px-3 py-4 text-[11px] font-bold uppercase text-on-surface-variant tracking-wider">Priority</th>
              <th className="px-3 py-4 text-[11px] font-bold uppercase text-on-surface-variant tracking-wider">Status</th>
              <th className="px-3 py-4 text-[11px] font-bold uppercase text-on-surface-variant tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant">
            {displayAlerts.map((alert, index) => (
              <tr key={index} className="hover:bg-surface-container-low transition-colors group">
                <td className="px-3 py-4 font-data-tabular font-medium text-on-surface leading-tight max-w-[140px]">{alert.vehicle_id || alert.vehicle_id_display || `VH-${alert.vehicle_id}`}</td>
                <td className="px-3 py-4 font-body-sm text-on-surface-variant leading-tight">{alert.service_type || alert.task}</td>
                <td className="px-3 py-4 font-body-sm text-on-surface whitespace-nowrap">{alert.due_date}</td>
                <td className="px-3 py-4 whitespace-nowrap">
                  <span className={`${getPriorityStyle(alert.priority)} px-2 py-1 rounded text-[11px] font-bold uppercase tracking-wider`}>
                    {alert.priority}
                  </span>
                </td>
                <td className="px-3 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${getStatusColorClass(alert.statusColor || 'outline')}`}></div>
                    <span className={`font-body-sm font-medium ${getStatusTextColor(alert.statusColor || 'outline')}`}>{alert.status}</span>
                  </div>
                </td>
                <td className="px-3 py-4 text-right">
                  <button className="text-on-surface-variant hover:text-primary transition-colors">
                    <span className="material-symbols-outlined text-[20px]">more_vert</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default MaintenanceTable;
