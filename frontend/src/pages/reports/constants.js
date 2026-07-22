export const MODULES = [
    { id: 'Vehicles', name: 'Vehicles', icon: 'directions_car' },
    { id: 'Drivers', name: 'Drivers', icon: 'person' },
    { id: 'Trips', name: 'Trips', icon: 'route' },
    { id: 'Maintenance', name: 'Maintenance', icon: 'build' },
    { id: 'Fuel', name: 'Fuel Log', icon: 'local_gas_station' },
    { id: 'Expenses', name: 'Expenses', icon: 'receipt_long' }
];

export const MODULE_FIELDS = {
    'Vehicles': [
        'id', 'registration_number', 'make', 'model', 'year', 'type', 'capacity',
        'current_odometer_km', 'status', 'created_at'
    ],
    'Drivers': [
        'id', 'license_number', 'license_type', 'license_expiry', 'status',
        'safety_score', 'total_trips', 'joined_date'
    ],
    'Trips': [
        'id', 'trip_number', 'vehicle_id', 'driver_id', 'start_time', 'end_time',
        'start_location', 'end_location', 'distance_km', 'status'
    ],
    'Maintenance': [
        'id', 'maintenance_number', 'vehicle_id', 'maintenance_type', 'description',
        'scheduled_date', 'completed_date', 'cost', 'priority', 'status'
    ],
    'Fuel': [
        'id', 'vehicle_id', 'trip_id', 'refuel_date', 'volume_liters', 'cost',
        'odometer_at_refuel', 'location'
    ],
    'Expenses': [
        'id', 'expense_type', 'amount', 'date', 'description', 'vehicle_id',
        'trip_id', 'maintenance_id', 'status'
    ]
};

export const OPERATORS = [
    'Equals', 'Contains', 'Greater Than', 'Less Than', 'Starts With', 'Ends With'
];

export const CHART_TYPES = [
    { id: 'table', name: 'Data Table', icon: 'table_chart' },
    { id: 'bar', name: 'Bar Chart', icon: 'bar_chart' },
    { id: 'line', name: 'Line Chart', icon: 'show_chart' },
    { id: 'pie', name: 'Pie Chart', icon: 'pie_chart' },
    { id: 'doughnut', name: 'Doughnut Chart', icon: 'donut_large' }
];
