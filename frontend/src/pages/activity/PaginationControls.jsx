import React from 'react';

const PaginationControls = ({ currentPage, totalItems, itemsPerPage, onPageChange, onPageSizeChange }) => {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  
  const handlePrev = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  return (
    <div className="mt-auto p-md border-t border-outline-variant flex flex-col md:flex-row items-center justify-between bg-surface-container-lowest gap-4">
      <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
        <span className="text-body-sm text-outline">Rows per page:</span>
        <select 
          value={itemsPerPage}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="bg-transparent border-none text-body-sm font-bold text-on-surface focus:ring-0 cursor-pointer outline-none"
        >
          <option value={5}>5</option>
          <option value={10}>10</option>
          <option value={25}>25</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
      </div>
      <div className="flex items-center gap-md">
        <span className="text-body-sm text-outline">
          {totalItems > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0}-
          {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems}
        </span>
        <div className="flex items-center gap-xs">
          <button 
            onClick={handlePrev}
            disabled={currentPage === 1 || totalItems === 0}
            className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
          >
            <span className="material-symbols-outlined">chevron_left</span>
          </button>
          <button 
            onClick={handleNext}
            disabled={currentPage === totalPages || totalPages === 0}
            className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
          >
            <span className="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PaginationControls;
