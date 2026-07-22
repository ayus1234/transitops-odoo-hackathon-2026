import React from 'react';

const NotificationBadge = ({ count }) => {
  if (!count || count <= 0) return null;
  
  const displayCount = count > 99 ? '99+' : count;
  
  return (
    <div className="absolute -top-1 -right-1 bg-error text-on-error text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center border-2 border-surface animate-fade-in z-10">
      {displayCount}
    </div>
  );
};

export default NotificationBadge;
