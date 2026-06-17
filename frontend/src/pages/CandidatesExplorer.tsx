import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import axios from 'axios';
import { Search, Filter, ChevronLeft, ChevronRight, Briefcase, MapPin, X } from 'lucide-react';
import CandidateProfileModal from '../components/CandidateProfileModal';

const API = 'http://127.0.0.1:8000';

const fetchCandidates = async (page: number, limit: number, search: string, skills: string, minExperience: string, currentRole: string) => {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (search) params.append('search', search);
  if (skills) params.append('skills', skills);
  if (minExperience) params.append('min_experience', minExperience);
  if (currentRole) params.append('current_role', currentRole);

  const res = await axios.get(`${API}/api/candidates?${params.toString()}`);
  return res.data;
};

export default function CandidatesExplorer() {
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');

  const [filterSkills, setFilterSkills] = useState('');
  const [filterMinExp, setFilterMinExp] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [activeFilters, setActiveFilters] = useState({ skills: '', minExp: '', role: '' });
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['candidates', page, limit, search, activeFilters],
    queryFn: () => fetchCandidates(page, limit, search, activeFilters.skills, activeFilters.minExp, activeFilters.role),
    placeholderData: (previousData) => previousData,
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
    <div className="flex-1 flex overflow-hidden relative z-10">
      {/* Sidebar Filters */}
      <div className="w-[280px] border-r border-white/[0.06] p-5 flex flex-col gap-5 overflow-y-auto shrink-0">
        <div>
          <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Filter size={16} className="text-slate-400" /> Filters
          </h2>
          <div className="space-y-4">
            <FilterInput label="Skills" placeholder="e.g. Python, React" value={filterSkills} onChange={setFilterSkills} />
            <FilterInput label="Min Experience (Yrs)" placeholder="0" value={filterMinExp} onChange={setFilterMinExp} type="number" />
            <FilterInput label="Current Role" placeholder="e.g. Engineer" value={filterRole} onChange={setFilterRole} />
            <div className="flex gap-2 pt-2">
              <button onClick={applyFilters} className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg font-medium text-sm transition-colors">
                Apply
              </button>
              <button onClick={clearFilters} className="flex-1 bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 py-2 rounded-lg font-medium text-sm transition-colors border border-white/[0.06]">
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Active Filters */}
        {(activeFilters.skills || activeFilters.minExp || activeFilters.role) && (
          <div className="pt-4 border-t border-white/[0.06]">
            <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-2 font-semibold">Active Filters</div>
            <div className="flex flex-wrap gap-1.5">
              {activeFilters.skills && <FilterTag label={`Skills: ${activeFilters.skills}`} onRemove={() => setActiveFilters(p => ({ ...p, skills: '' }))} />}
              {activeFilters.minExp && <FilterTag label={`Exp ≥ ${activeFilters.minExp}y`} onRemove={() => setActiveFilters(p => ({ ...p, minExp: '' }))} />}
              {activeFilters.role && <FilterTag label={`Role: ${activeFilters.role}`} onRemove={() => setActiveFilters(p => ({ ...p, role: '' }))} />}
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="p-5 border-b border-white/[0.06] flex items-center justify-between glass-strong">
          <h1 className="text-xl font-bold text-white">Dataset Explorer</h1>
          <form onSubmit={handleSearch} className="relative w-80">
            <input
              type="text"
              className="w-full pl-10 pr-4 py-2.5 glass-input rounded-xl text-sm"
              placeholder="Search by name, skills, company..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <Search className="absolute left-3.5 top-3 text-slate-500" size={16} />
          </form>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full text-slate-500 text-sm">
              <div className="flex flex-col items-center gap-3">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                Loading dataset...
              </div>
            </div>
          ) : isError ? (
            <div className="flex items-center justify-center h-full text-rose-400 text-sm">Error loading data. Is the backend running?</div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead className="glass-strong sticky top-0 z-10 border-b border-white/[0.06]">
                <tr>
                  <th className="py-3 px-6 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Candidate</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Experience</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Current Role</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Location</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {data?.data?.map((candidate: any, i: number) => (
                  <motion.tr
                    key={candidate.candidate_id}
                    className="hover:bg-white/[0.03] transition-colors group"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                  >
                    <td className="py-3.5 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 text-slate-300 flex items-center justify-center font-bold text-xs">
                          {candidate.profile?.anonymized_name?.charAt(0) || "U"}
                        </div>
                        <div>
                          <div className="font-semibold text-white text-sm">{candidate.profile?.anonymized_name || "Unknown"}</div>
                          <div className="text-[10px] text-slate-600 truncate max-w-[200px]">{candidate.profile?.headline}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-6">
                      <div className="flex items-center gap-2 text-slate-400 text-sm">
                        <Briefcase size={14} className="text-slate-600" />
                        {candidate.profile?.years_of_experience || 0}y
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-slate-400 text-sm">
                      {candidate.profile?.current_title || "N/A"}
                      <div className="text-[10px] text-slate-600">{candidate.profile?.current_company}</div>
                    </td>
                    <td className="py-3.5 px-6 text-slate-400 text-sm">
                      <div className="flex items-center gap-2">
                        <MapPin size={14} className="text-slate-600" />
                        {candidate.profile?.location || "N/A"}
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      <button
                        onClick={() => setSelectedCandidateId(candidate.candidate_id)}
                        className="text-blue-400 hover:text-blue-300 font-medium text-xs opacity-0 group-hover:opacity-100 transition-all px-3 py-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20"
                      >
                        View Profile
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        <div className="border-t border-white/[0.06] p-4 glass-strong flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span>Page {data?.page} of {data?.total_pages}</span>
            <span className="text-slate-600">({data?.total?.toLocaleString()} total)</span>
            <select
              value={limit}
              onChange={(e) => { setLimit(Number(e.target.value)); setPage(1); }}
              className="glass-input rounded-lg p-1.5 text-xs"
            >
              <option value={25}>25/page</option>
              <option value={50}>50/page</option>
              <option value={100}>100/page</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 glass rounded-lg hover:bg-white/[0.06] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={14} className="text-slate-400" />
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= (data?.total_pages || 1)}
              className="p-2 glass rounded-lg hover:bg-white/[0.06] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight size={14} className="text-slate-400" />
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

function FilterInput({ label, placeholder, value, onChange, type = 'text' }: {
  label: string; placeholder: string; value: string; onChange: (v: string) => void; type?: string;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-500 mb-1.5">{label}</label>
      <input
        type={type}
        className="w-full glass-input rounded-lg p-2.5 text-sm"
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
      />
    </div>
  );
}

function FilterTag({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="flex items-center gap-1 px-2 py-1 text-[10px] font-medium rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
      {label}
      <button onClick={onRemove} className="hover:text-white transition-colors"><X size={10} /></button>
    </span>
  );
}
