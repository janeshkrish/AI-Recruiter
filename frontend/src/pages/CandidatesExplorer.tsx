import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Search, Filter, ChevronLeft, ChevronRight, User, Briefcase, MapPin } from 'lucide-react';
import CandidateProfileModal from '../components/CandidateProfileModal';

const fetchCandidates = async (page: number, limit: number, search: string, skills: string, minExperience: string, currentRole: string) => {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (search) params.append('search', search);
  if (skills) params.append('skills', skills);
  if (minExperience) params.append('min_experience', minExperience);
  if (currentRole) params.append('current_role', currentRole);
  
  const res = await axios.get(`http://127.0.0.1:8000/api/candidates?${params.toString()}`);
  return res.data;
};

export default function CandidatesExplorer() {
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  
  // Advanced filters state
  const [filterSkills, setFilterSkills] = useState('');
  const [filterMinExp, setFilterMinExp] = useState('');
  const [filterRole, setFilterRole] = useState('');

  const [activeFilters, setActiveFilters] = useState({ skills: '', minExp: '', role: '' });

  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['candidates', page, limit, search, activeFilters],
    queryFn: () => fetchCandidates(page, limit, search, activeFilters.skills, activeFilters.minExp, activeFilters.role),
    placeholderData: (previousData) => previousData, // keep old data while fetching
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearch(searchInput);
  };

  const applyFilters = () => {
    setPage(1);
    setActiveFilters({ skills: filterSkills, minExp: filterMinExp, role: filterRole });
  };
  
  const clearFilters = () => {
    setFilterSkills('');
    setFilterMinExp('');
    setFilterRole('');
    setActiveFilters({ skills: '', minExp: '', role: '' });
    setPage(1);
  };

  return (
    <div className="flex-1 flex overflow-hidden bg-[#FAFAFA]">
      {/* Sidebar Filters */}
      <div className="w-[300px] border-r border-slate-200 bg-white p-6 flex flex-col gap-6 overflow-y-auto">
        <div>
          <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Filter size={18} /> Advanced Filters
          </h2>
          {/* Mock filters for UI */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Skills</label>
              <input type="text" className="w-full border border-slate-300 rounded-md p-2 text-sm" placeholder="e.g. Python, React" value={filterSkills} onChange={e => setFilterSkills(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Min Experience (Yrs)</label>
              <input type="number" className="w-full border border-slate-300 rounded-md p-2 text-sm" placeholder="0" value={filterMinExp} onChange={e => setFilterMinExp(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Current Role</label>
              <input type="text" className="w-full border border-slate-300 rounded-md p-2 text-sm" placeholder="e.g. Engineer" value={filterRole} onChange={e => setFilterRole(e.target.value)} />
            </div>
            <div className="flex gap-2 pt-2">
              <button onClick={applyFilters} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md font-medium text-sm transition-colors">
                Apply
              </button>
              <button onClick={clearFilters} className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 py-2 rounded-md font-medium text-sm transition-colors border border-slate-200">
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content: Table */}
      <div className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Header */}
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-800">Dataset Explorer</h1>
          <form onSubmit={handleSearch} className="relative w-96">
            <input 
              type="text" 
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
              placeholder="Search by name, skills, company..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
          </form>
        </div>

        {/* Table Area */}
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full text-slate-500">Loading massive dataset...</div>
          ) : isError ? (
            <div className="flex items-center justify-center h-full text-red-500">Error loading data.</div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 sticky top-0 z-10 border-b border-slate-200">
                <tr>
                  <th className="py-3 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Candidate</th>
                  <th className="py-3 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Experience</th>
                  <th className="py-3 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Current Role</th>
                  <th className="py-3 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Location</th>
                  <th className="py-3 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data?.data?.map((candidate: any) => (
                  <tr key={candidate.candidate_id} className="hover:bg-slate-50 transition-colors group">
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                          {candidate.profile?.anonymized_name?.charAt(0) || "U"}
                        </div>
                        <div>
                          <div className="font-semibold text-slate-800">{candidate.profile?.anonymized_name || "Unknown Candidate"}</div>
                          <div className="text-xs text-slate-500 truncate max-w-[200px]">{candidate.profile?.headline}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-2 text-slate-600">
                        <Briefcase size={16} className="text-slate-400" />
                        {candidate.profile?.years_of_experience || 0} years
                      </div>
                    </td>
                    <td className="py-4 px-6 text-slate-600">
                      {candidate.profile?.current_title || "N/A"}
                      <div className="text-xs text-slate-400">{candidate.profile?.current_company}</div>
                    </td>
                    <td className="py-4 px-6 text-slate-600">
                      <div className="flex items-center gap-2">
                        <MapPin size={16} className="text-slate-400" />
                        {candidate.profile?.location || "N/A"}
                      </div>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <button 
                        onClick={() => setSelectedCandidateId(candidate.candidate_id)}
                        className="text-blue-600 hover:text-blue-800 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        View Profile
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination Footer */}
        <div className="border-t border-slate-200 p-4 bg-white flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-slate-600">
            <span>Showing page {data?.page} of {data?.total_pages}</span>
            <span>({data?.total?.toLocaleString()} total candidates)</span>
            <select 
              value={limit} 
              onChange={(e) => { setLimit(Number(e.target.value)); setPage(1); }}
              className="border border-slate-300 rounded p-1"
            >
              <option value={25}>25 per page</option>
              <option value={50}>50 per page</option>
              <option value={100}>100 per page</option>
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={16} />
            </button>
            <button 
              onClick={() => setPage(p => p + 1)}
              disabled={page >= (data?.total_pages || 1)}
              className="p-2 border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
      
      {selectedCandidateId && (
        <CandidateProfileModal 
          candidateId={selectedCandidateId} 
          onClose={() => setSelectedCandidateId(null)} 
        />
      )}
    </div>
  );
}
