import React, { useEffect, useState } from 'react';
import api from '../services/api';

const GenericList = ({ title, apiEndpoint, columns, renderRow }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(apiEndpoint);
        setData(response.data.data);
      } catch (error) {
        console.error(`Error fetching ${title}`, error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [apiEndpoint, title]);

  return (
    <div className="p-gutter flex flex-col gap-gutter flex-1 mt-4">
      <h1 className="font-headline-md text-headline-md font-bold mb-4 px-md">{title}</h1>
      <div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col min-w-0 mx-md mb-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-surface-container text-label-caps text-on-surface-variant uppercase tracking-wider font-bold border-b border-outline-variant">
                {columns.map((col, idx) => <th key={idx} className="px-md py-3.5">{col}</th>)}
              </tr>
            </thead>
            <tbody className="text-body-sm">
              {loading ? (
                <tr>
                  <td colSpan={columns.length} className="text-center py-8">Loading {title}...</td>
                </tr>
              ) : data.map(renderRow)}
              {data.length === 0 && !loading && (
                <tr>
                  <td colSpan={columns.length} className="text-center py-8 text-on-surface-variant">No records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default GenericList;
