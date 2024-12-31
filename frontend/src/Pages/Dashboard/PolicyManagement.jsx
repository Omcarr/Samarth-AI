import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Upload, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Search, 
  Filter 
} from 'lucide-react';
import { Link } from 'react-router-dom';

// Simulated policy data structure
const initialPolicies = [
  {
    id: 1,
    title: 'Remote Work Policy',
    department: 'HR',
    uploadDate: '2024-02-15',
    status: 'pending',
    uploadedBy: 'John Doe',
    documentUrl: '/sample-policy.pdf'
  },
  {
    id: 2,
    title: 'Cybersecurity Guidelines',
    department: 'IT',
    uploadDate: '2024-01-20',
    status: 'approved',
    uploadedBy: 'Jane Smith',
    documentUrl: '/cybersecurity-policy.pdf'
  },
  {
    id: 3,
    title: 'Expense Reimbursement Policy',
    department: 'Finance',
    uploadDate: '2024-03-10',
    status: 'rejected',
    uploadedBy: 'Mike Johnson',
    documentUrl: '/expense-policy.pdf'
  }
];

const PolicyManagement = () => {
  const [policies, setPolicies] = useState(initialPolicies);
  const [filteredPolicies, setFilteredPolicies] = useState(initialPolicies);
  const [searchTerm, setSearchTerm] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  // Departments and statuses for filtering
  const departments = ['All', 'HR', 'Finance', 'IT', 'Sales', 'Marketing', 'Operations', 'Legal'];
  const statuses = ['All', 'pending', 'approved', 'rejected'];

  // Filter policies based on search and filters
  useEffect(() => {
    let result = policies.filter(policy => 
      (searchTerm === '' || 
        policy.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        policy.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
        policy.uploadedBy.toLowerCase().includes(searchTerm.toLowerCase())
      ) &&
      (departmentFilter === 'All' || policy.department === departmentFilter) &&
      (statusFilter === 'All' || policy.status === statusFilter)
    );

    setFilteredPolicies(result);
  }, [searchTerm, departmentFilter, statusFilter, policies]);

  // Handle policy approval
  const handleApprove = (policyId) => {
    const updatedPolicies = policies.map(policy => 
      policy.id === policyId 
        ? { ...policy, status: 'approved' } 
        : policy
    );
    setPolicies(updatedPolicies);
  };

  // Handle policy rejection
  const handleReject = (policyId) => {
    const updatedPolicies = policies.map(policy => 
      policy.id === policyId 
        ? { ...policy, status: 'rejected' } 
        : policy
    );
    setPolicies(updatedPolicies);
  };

  // Status color and icon mapping
  const getStatusStyle = (status) => {
    switch(status) {
      case 'approved':
        return {
          color: 'text-zinc-900',
          icon: <CheckCircle className="mr-2 text-zinc-900" />,
          bg: 'bg-green-50'
        };
      case 'rejected':
        return {
          color: 'text-zinc-900',
          icon: <XCircle className="mr-2 text-zinc-900" />,
          bg: 'bg-red-50'
        };
      default:
        return {
          color: 'text-zinc-900',
          icon: <Clock className="mr-2 text-zinc-900" />,
          bg: 'bg-yellow-50'
        };
    }
  };

  return (
    <div className="md:-mt-8 min-h-screen bg-gray-50 text-zinc-900 p-8">
      <div className="container mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold flex items-center text-zinc-900">
            <FileText className="mr-4" /> Policy Management
          </h1>
        </div>

        {/* Filters and Search */}
        <div className="bg-white text-zinc-900 shadow-md rounded-lg p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search Input */}
            <div className="relative">
              <input 
                type="text"
                placeholder="Search policies..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 bg-white text-zinc-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-zinc-900"
              />
              <Search className="absolute left-3 top-3 text-gray-400" />
            </div>

            {/* Department Filter */}
            <div className="relative">
              <select
                value={departmentFilter}
                onChange={(e) => setDepartmentFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 bg-white text-zinc-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-zinc-900"
              >
                {departments.map(dept => (
                  <option 
                    key={dept} 
                    value={dept} 
                    className="bg-white text-zinc-900"
                  >
                    {dept}
                  </option>
                ))}
              </select>
              <Filter className="absolute left-3 top-3 text-gray-400" />
            </div>

            {/* Status Filter */}
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 bg-white text-zinc-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-zinc-900"
              >
                {statuses.map(status => (
                  <option 
                    key={status} 
                    value={status}
                    className="bg-white text-zinc-900"
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </option>
                ))}
              </select>
              <Filter className="absolute left-3 top-3 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Policies List */}
        <div className="space-y-4">
          {filteredPolicies.length === 0 ? (
            <div className="bg-white text-zinc-900 shadow-md rounded-lg p-6 text-center">
              No policies found
            </div>
          ) : (
            filteredPolicies.map(policy => {
              const statusStyle = getStatusStyle(policy.status);
              return (
                <div 
                  key={policy.id} 
                  className={`bg-white text-zinc-900 shadow-md rounded-lg p-6 flex items-center justify-between ${statusStyle.bg}`}
                >
                  <div className="flex items-center space-x-4">
                    {statusStyle.icon}
                    <div>
                      <h3 className="text-xl font-semibold text-zinc-900">
                        {policy.title}
                      </h3>
                      <p className="text-gray-600">
                        Department: {policy.department} | 
                        Uploaded: {policy.uploadDate} | 
                        By: {policy.uploadedBy}
                      </p>
                      <span className={`font-medium ${statusStyle.color} capitalize`}>
                        {policy.status}
                      </span>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <a 
                      href={policy.documentUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="bg-zinc-100 text-zinc-900 hover:bg-zinc-200 px-3 py-2 rounded-lg transition-colors"
                    >
                      View Document
                    </a>
                    
                    {policy.status === 'pending' && (
                      <>
                        <button 
                          onClick={() => handleApprove(policy.id)}
                          className="bg-green-100 text-zinc-900 hover:bg-green-200 px-3 py-2 rounded-lg transition-colors"
                        >
                          Approve
                        </button>
                        <button 
                          onClick={() => handleReject(policy.id)}
                          className="bg-red-100 text-zinc-900 hover:bg-red-200 px-3 py-2 rounded-lg transition-colors"
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default PolicyManagement;