import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { Search, Filter, ChevronLeft, ChevronRight, Briefcase, MapPin, X, Download, Sparkles, ArrowLeft, Trophy } from 'lucide-react';
import AutocompleteInput from '../components/AutocompleteInput';

const API = 'http://127.0.0.1:8000';

interface RoleRankingRow {
  candidate_id: string;
  rank: number;
  score: number;
  reasoning: string;
  candidate?: {
    name?: string;
    current_title?: string;
    years_of_experience?: number;
    location?: string;
    current_company?: string;
    core_hits?: number;
  };
}

interface RoleRankingResponse {
  role: string;
  total: number;
  rows: RoleRankingRow[];
}

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

// Fetch a large batch to extract unique skills/roles for autocomplete suggestions
const fetchSuggestionData = async () => {
  const res = await axios.get(`${API}/api/candidates?page=1&limit=500`);
  return res.data;
};

const fetchRoleRanking = async (): Promise<RoleRankingResponse> => {
  const res = await axios.get(`${API}/api/candidates/role-ranking?limit=100`);
  return res.data;
};

export default function CandidatesExplorer() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);
  const [showRoleRanking, setShowRoleRanking] = useState(false);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');

  const [filterSkills, setFilterSkills] = useState('');
  const [filterMinExp, setFilterMinExp] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [activeFilters, setActiveFilters] = useState({ skills: '', minExp: '', role: '' });

  const { data, isLoading, isError } = useQuery({
    queryKey: ['candidates', page, limit, search, activeFilters],
    queryFn: () => fetchCandidates(page, limit, search, activeFilters.skills, activeFilters.minExp, activeFilters.role),
    placeholderData: (previousData) => previousData,
  });

  const {
    data: roleRankingData,
    isFetching: isRankingLoading,
    isError: isRankingError,
    refetch: refetchRoleRanking,
  } = useQuery({
    queryKey: ['role-ranking', 100],
    queryFn: fetchRoleRanking,
    enabled: false,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch suggestion data for autocomplete
  const { data: suggestionData } = useQuery({
    queryKey: ['candidate-suggestions'],
    queryFn: fetchSuggestionData,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Extract unique skills and roles from fetched data
  const { uniqueSkills, uniqueRoles } = useMemo(() => {
    if (!suggestionData?.data) return { uniqueSkills: [] as string[], uniqueRoles: [] as string[] };

    const skillsSet = new Set<string>();
    const rolesSet = new Set<string>();

    for (const candidate of suggestionData.data) {
      // Extract skills
      const candidateSkills = candidate.skills || [];
      for (const skill of candidateSkills) {
        const name = typeof skill === 'string' ? skill : skill.name;
        if (name) skillsSet.add(name);
      }

      // Extract roles
      const title = candidate.profile?.current_title;
      if (title) rolesSet.add(title);
    }

    return {
      uniqueSkills: Array.from(skillsSet).sort(),
      uniqueRoles: Array.from(rolesSet).sort(),
    };
  }, [suggestionData]);

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

  const handleGenerateRoleRanking = () => {
    setShowRoleRanking(true);
    void refetchRoleRanking();
  };

  const handleDownloadRanking = () => {
    window.location.href = `${API}/api/candidates/role-ranking.csv?limit=100`;
  };

  return (
    <div className="flex-1 flex overflow-hidden relative z-10">
      {/* Sidebar Filters */}
      <div className="w-[280px] border-r border-[#7a5647]/10 p-5 flex flex-col gap-5 overflow-y-auto shrink-0 bg-[rgba(251,244,236,0.7)]">
        <div>
          <h2 className="text-sm font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
            <Filter size={16} className="text-[#8a5a45]" /> Filters
          </h2>
          <div className="space-y-4">
            <AutocompleteInput
              label="Skills"
              placeholder="e.g. Python, React"
              value={filterSkills}
              onChange={setFilterSkills}
              suggestions={uniqueSkills}
            />
            <FilterInput label="Min Experience (Yrs)" placeholder="0" value={filterMinExp} onChange={setFilterMinExp} type="number" />
            <AutocompleteInput
              label="Current Role"
              placeholder="e.g. Engineer"
              value={filterRole}
              onChange={setFilterRole}
              suggestions={uniqueRoles}
            />
            <div className="flex gap-2 pt-2">
              <button onClick={applyFilters} className="metal-button flex-1 py-2 rounded-lg font-medium text-sm">
                Apply
              </button>
              <button onClick={clearFilters} className="metal-button-secondary flex-1 py-2 rounded-lg font-medium text-sm">
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Active Filters */}
        {(activeFilters.skills || activeFilters.minExp || activeFilters.role) && (
          <div className="pt-4 border-t border-[#7a5647]/10">
            <div className="text-[10px] text-[var(--color-text-tertiary)] uppercase tracking-wider mb-2 font-semibold">Active Filters</div>
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
        <div className="p-5 border-b border-[#7a5647]/10 flex flex-wrap items-center justify-between gap-3 glass-strong">
          <div className="flex items-center gap-3">
            {showRoleRanking && (
              <button
                type="button"
                onClick={() => setShowRoleRanking(false)}
                className="p-2 glass rounded-lg hover:bg-white transition-colors"
                title="Back to dataset"
              >
                <ArrowLeft size={16} className="text-[#8b766c]" />
              </button>
            )}
            <div>
              <h1 className="text-xl font-bold text-[var(--color-text-primary)]">
                {showRoleRanking ? 'Senior AI Engineer Ranking' : 'Dataset Explorer'}
              </h1>
              {showRoleRanking && (
                <div className="text-[10px] text-[var(--color-text-tertiary)] uppercase tracking-wider font-semibold">
                  {roleRankingData?.total || 100} ranked candidates
                </div>
              )}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {!showRoleRanking && (
              <form onSubmit={handleSearch} className="relative w-80">
                <input
                  type="text"
                  className="w-full pl-10 pr-4 py-2.5 glass-input rounded-xl text-sm"
                  placeholder="Search by name, skills, company..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                />
                <Search className="absolute left-3.5 top-3 text-[#8b766c]" size={16} />
              </form>
            )}
            <button
              type="button"
              onClick={handleGenerateRoleRanking}
              disabled={isRankingLoading}
              className="metal-button inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm"
              title="Generate role ranking"
            >
              <Sparkles size={16} />
              {isRankingLoading ? 'Analyzing...' : 'Role Ranking'}
            </button>
            <button
              type="button"
              onClick={handleDownloadRanking}
              className="metal-button-secondary inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm"
              title="Download CSV"
            >
              <Download size={16} />
              Download CSV
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          {showRoleRanking ? (
            isRankingLoading && !roleRankingData ? (
              <div className="flex items-center justify-center h-full text-[var(--color-text-tertiary)] text-sm">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-6 h-6 border-2 border-[#b15c3e] border-t-transparent rounded-full animate-spin" />
                  Building role ranking...
                </div>
              </div>
            ) : isRankingError ? (
              <div className="flex items-center justify-center h-full text-rose-400 text-sm">Error building role ranking. Is the backend running?</div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead className="glass-strong sticky top-0 z-10 border-b border-[#7a5647]/10">
                  <tr>
                    <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider w-[90px]">Rank</th>
                    <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider w-[260px]">Candidate ID</th>
                    <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider w-[120px]">Score</th>
                    <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider min-w-[460px]">Reasoning</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#7a5647]/8">
                  {roleRankingData?.rows?.map((row, i) => (
                    <motion.tr
                      key={row.candidate_id}
                      className="hover:bg-[#fff8f1] transition-colors group"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: Math.min(i * 0.01, 0.25) }}
                    >
                      <td className="py-3.5 px-6">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-black ${
                          row.rank === 1 ? 'rank-gold' : row.rank === 2 ? 'rank-silver' : row.rank === 3 ? 'rank-bronze' : 'bg-[var(--color-pill-bg)] text-[var(--color-pill-text)] border border-[var(--color-pill-border)]'
                        }`}>
                          {row.rank <= 3 ? <Trophy size={16} /> : row.rank}
                        </div>
                      </td>
                      <td className="py-3.5 px-6">
                        <button
                          type="button"
                          onClick={() => navigate(`/candidate/${row.candidate_id}`, { state: { returnTo: '/candidates' } })}
                          className="font-semibold text-[var(--color-text-primary)] text-sm hover:text-[var(--color-accent-blue)] transition-colors text-left"
                        >
                          {row.candidate_id}
                        </button>
                        <div className="text-[10px] text-[var(--color-text-tertiary)] truncate max-w-[220px]">
                          {row.candidate?.current_title || 'Professional'} {row.candidate?.years_of_experience ? `- ${row.candidate.years_of_experience.toFixed(1)}y` : ''}
                        </div>
                      </td>
                      <td className="py-3.5 px-6">
                        <span className="inline-flex items-center justify-center min-w-[70px] px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-700 border border-emerald-500/20 font-mono text-sm font-bold">
                          {row.score.toFixed(3)}
                        </span>
                      </td>
                      <td className="py-3.5 px-6 text-[var(--color-text-secondary)] text-sm leading-relaxed">
                        {row.reasoning}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            )
          ) : isLoading ? (
            <div className="flex items-center justify-center h-full text-[var(--color-text-tertiary)] text-sm">
              <div className="flex flex-col items-center gap-3">
                <div className="w-6 h-6 border-2 border-[#b15c3e] border-t-transparent rounded-full animate-spin" />
                Loading dataset...
              </div>
            </div>
          ) : isError ? (
            <div className="flex items-center justify-center h-full text-rose-400 text-sm">Error loading data. Is the backend running?</div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead className="glass-strong sticky top-0 z-10 border-b border-[#7a5647]/10">
                <tr>
                  <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">Candidate</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">Experience</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">Current Role</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">Location</th>
                  <th className="py-3 px-6 text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#7a5647]/8">
                {data?.data?.map((candidate: any, i: number) => (
                  <motion.tr
                    key={candidate.candidate_id}
                    className="hover:bg-[#fff8f1] transition-colors group"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                  >
                    <td className="py-3.5 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#b15c3e] to-[#d89457] text-[#fff9f4] flex items-center justify-center font-bold text-xs">
                          {candidate.profile?.anonymized_name?.charAt(0) || "U"}
                        </div>
                        <div>
                          <button
                            type="button"
                            onClick={() => navigate(`/candidate/${candidate.candidate_id}`)}
                            className="font-semibold text-[var(--color-text-primary)] text-sm hover:text-[var(--color-accent-blue)] transition-colors text-left"
                          >
                            {candidate.profile?.anonymized_name || "Unknown"}
                          </button>
                          <div className="text-[10px] text-[var(--color-text-tertiary)] truncate max-w-[200px]">{candidate.profile?.headline}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-6">
                      <div className="flex items-center gap-2 text-[var(--color-text-secondary)] text-sm">
                        <Briefcase size={14} className="text-[#b15c3e]" />
                        {candidate.profile?.years_of_experience || 0}y
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-[var(--color-text-secondary)] text-sm">
                      {candidate.profile?.current_title || "N/A"}
                      <div className="text-[10px] text-[var(--color-text-tertiary)]">{candidate.profile?.current_company}</div>
                    </td>
                    <td className="py-3.5 px-6 text-[var(--color-text-secondary)] text-sm">
                      <div className="flex items-center gap-2">
                        <MapPin size={14} className="text-[#0f766e]" />
                        {candidate.profile?.location || "N/A"}
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-right" />
                  </motion.tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {!showRoleRanking && (
        <div className="border-t border-[#7a5647]/10 p-4 glass-strong flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-[var(--color-text-tertiary)]">
            <span>Page {data?.page} of {data?.total_pages}</span>
            <span className="text-[var(--color-text-tertiary)]">({data?.total?.toLocaleString()} total)</span>
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
              className="p-2 glass rounded-lg hover:bg-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={14} className="text-[#8b766c]" />
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= (data?.total_pages || 1)}
              className="p-2 glass rounded-lg hover:bg-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight size={14} className="text-[#8b766c]" />
            </button>
          </div>
        </div>
        )}
      </div>
    </div>
  );
}

function FilterInput({ label, placeholder, value, onChange, type = 'text' }: {
  label: string; placeholder: string; value: string; onChange: (v: string) => void; type?: string;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-[var(--color-text-tertiary)] mb-1.5">{label}</label>
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
    <span className="flex items-center gap-1 px-2 py-1 text-[10px] font-medium rounded-md bg-[var(--color-pill-bg)] text-[var(--color-pill-text)] border border-[var(--color-pill-border)]">
      {label}
      <button onClick={onRemove} className="hover:text-[var(--color-accent-blue)] transition-colors"><X size={10} /></button>
    </span>
  );
}
