import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import DocumentUpload from '../DocumentUpload';
import DocumentSearch from '../DocumentSearch';

const MainLayout = () => {
  return (
    <div className="flex h-screen bg-gray-100">
      <aside className="w-64 bg-white shadow-md">
        <div className="p-4">
          <h1 className="text-2xl font-bold text-gray-800">NeoBoi</h1>
        </div>
        <nav>
          <ul>
            <li className="p-4 hover:bg-gray-200">
              <Link to="/" className="text-gray-700">Graph</Link>
            </li>
            <li className="p-4 hover:bg-gray-200">
              <Link to="/unstructured" className="text-gray-700">Unstructured Data</Link>
            </li>
          </ul>
        </nav>
      </aside>
      <main className="flex-1 p-4">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
