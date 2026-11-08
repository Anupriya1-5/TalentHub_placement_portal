import { Briefcase, CheckCircle2, GraduationCap, XCircle, Upload, Sparkles, Target, CalendarDays } from 'lucide-react';
import { useEffect, useState } from 'react';
import api from '../api.js';
import StatusBadge from '../components/StatusBadge.jsx';

export default function StudentDashboard() {
  const [profile, setProfile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [skills, setSkills] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [interviews, setInterviews] = useState([]);
  const [skillGap, setSkillGap] = useState(null);
  const [message, setMessage] = useState(null);
  const [uploading, setUploading] = useState(false);

  const loadAll = async () => {
    const [profileRes, jobsRes, appsRes, skillsRes, recRes, interviewRes] = await Promise.all([
      api.get('/students/me'), api.get('/jobs'), api.get('/applications/me'),
      api.get('/students/me/skills'), api.get('/students/me/recommendations'), api.get('/interviews/calendar')
    ]);
    setProfile(profileRes.data); setJobs(jobsRes.data); setApplications(appsRes.data);
    setSkills(skillsRes.data.skills || []); setRecommendations(recRes.data); setInterviews(interviewRes.data);
  };
  useEffect(() => { loadAll().catch(() => setMessage({ ok: false, text: 'Could not load dashboard data.' })); }, []);
  const appliedJobIds = new Set(applications.map((a) => a.job_id));
  const apply = async (jobId) => { setMessage(null); try { await api.post('/applications', { job_id: jobId }); setMessage({ ok: true, text: 'Application submitted successfully!' }); await loadAll(); } catch (err) { setMessage({ ok: false, text: err?.response?.data?.detail || 'Could not submit application.' }); } };
  const respondToOffer = async (applicationId, accept) => { await api.patch(`/offers/${applicationId}/respond`, { accept }); await loadAll(); };
  const uploadResume = async (event) => {
    const file = event.target.files?.[0]; if (!file) return;
    const form = new FormData(); form.append('file', file); setUploading(true); setMessage(null);
    try { const result = await api.post('/students/me/resume', form, { headers: { 'Content-Type': 'multipart/form-data' } }); setSkills(result.data.skills); setMessage({ ok: true, text: `Resume analyzed. ${result.data.skill_count} skills detected.` }); const rec = await api.get('/students/me/recommendations'); setRecommendations(rec.data); }
    catch (err) { setMessage({ ok: false, text: err?.response?.data?.detail || 'Resume analysis failed.' }); }
    finally { setUploading(false); event.target.value = ''; }
  };
  const showGap = async (jobId) => { const result = await api.get(`/students/me/skill-gap/${jobId}`); setSkillGap(result.data); };
  if (!profile) return <p className="text-slate-400">Loading...</p>;
  return <div className="space-y-6">
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 space-y-4"><div className="flex items-center gap-2 text-indigo-400 text-xl font-semibold"><GraduationCap /> Student Portal ({profile.name})</div><div className="grid grid-cols-3 gap-4 text-sm bg-slate-900/50 p-4 rounded-lg"><div><span className="text-slate-400">Branch:</span> {profile.branch}</div><div><span className="text-slate-400">CGPA:</span> {profile.cgpa}</div><div><span className="text-slate-400">Active Backlogs:</span> {profile.active_backlogs}</div></div></div>
    {message && <div className={`p-4 rounded-lg flex items-center gap-3 ${message.ok ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800' : 'bg-rose-950/80 text-rose-300 border border-rose-800'}`}>{message.ok ? <CheckCircle2 /> : <XCircle />}<span>{message.text}</span></div>}

    <section className="bg-slate-800 p-6 rounded-xl border border-slate-700 space-y-4"><div className="flex items-center gap-2 text-indigo-300 text-lg font-semibold"><Upload /> Resume Analyzer</div><p className="text-sm text-slate-400">Upload a text-based PDF resume (maximum 5 MB). TalentHub extracts skills and uses them for job recommendations.</p><label className="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 px-4 py-2 text-sm font-medium">{uploading ? 'Analyzing...' : 'Upload PDF Resume'}<input type="file" accept="application/pdf,.pdf" onChange={uploadResume} disabled={uploading} className="hidden" /></label>{skills.length > 0 ? <div><p className="text-sm text-slate-300 mb-2">Detected skills ({skills.length})</p><div className="flex flex-wrap gap-2">{skills.map(s => <span key={s} className="text-xs rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 px-3 py-1">{s}</span>)}</div></div> : <p className="text-xs text-amber-300">No resume analyzed yet. Upload one to activate personalized matching.</p>}</section>

    <section className="bg-slate-800 p-6 rounded-xl border border-slate-700 space-y-4"><div className="flex items-center gap-2 text-indigo-300 text-lg font-semibold"><Sparkles /> Smart Job Matching</div><p className="text-xs text-slate-400">Match score is based on overlap between your extracted skills and skills mentioned in the job title/description. Eligibility also checks CGPA and backlogs.</p><div className="space-y-3">{recommendations.map(r => <div key={r.job_id} className="bg-slate-900 rounded-lg p-4"><div className="flex flex-wrap justify-between gap-2"><div><div className="font-medium">{r.company_name} — {r.role_title}</div><div className="text-xs text-slate-400 mt-1">{r.package_lpa} LPA · {r.eligible ? 'Eligible' : 'Not eligible by academic criteria'}</div></div><div className="text-right"><div className="text-xl font-bold text-indigo-300">{r.match_score}%</div><div className="text-xs text-slate-500">Skill match</div></div></div><div className="h-2 bg-slate-700 rounded-full mt-3 overflow-hidden"><div className="h-full bg-indigo-500" style={{width:`${r.match_score}%`}} /></div><div className="flex flex-wrap gap-2 mt-3"><button onClick={() => showGap(r.job_id)} className="text-xs px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600">View skill gap</button>{appliedJobIds.has(r.job_id) ? <span className="text-xs text-slate-400 px-2 py-1.5">Already applied</span> : <button disabled={!r.eligible} onClick={() => apply(r.job_id)} className="text-xs px-3 py-1.5 rounded bg-indigo-600 disabled:opacity-40">Apply</button>}</div></div>)}{recommendations.length===0 && <p className="text-sm text-slate-400">No recommendations available.</p>}</div>
      {skillGap && <div className="border border-indigo-800 bg-slate-900 rounded-lg p-4"><div className="font-semibold mb-2"><Target className="inline w-4 h-4 mr-1"/> Skill gap: {skillGap.role_title}</div><p className="text-xs text-emerald-300 mb-2">Skills you have: {skillGap.your_skills.join(', ') || 'None detected for this role'}</p><p className="text-xs text-amber-300">Skills to develop: {skillGap.missing_skills.join(', ') || 'No missing skills identified from the job description'}</p></div>}
    </section>

    <section className="bg-slate-800 p-6 rounded-xl border border-slate-700"><h3 className="font-semibold text-lg flex items-center gap-2 mb-4"><CalendarDays className="w-5 h-5 text-indigo-400"/> Interview Schedule</h3><div className="space-y-2">{interviews.map(i => <div key={i.id} className="bg-slate-900 p-3 rounded-lg flex flex-wrap justify-between gap-2 text-sm"><div><div className="font-medium">{i.company_name} — {i.role_title}</div><div className="text-xs text-slate-400">{new Date(i.scheduled_at).toLocaleString()}</div></div><StatusBadge status={i.result}/></div>)}{interviews.length===0 && <p className="text-sm text-slate-400">No interviews scheduled.</p>}</div></section>

    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700"><h3 className="font-semibold text-lg flex items-center gap-2 mb-4"><Briefcase className="w-5 h-5 text-indigo-400"/> Job Listings</h3><div className="space-y-3">{jobs.map(job => <div key={job.id} className="bg-slate-900 p-4 rounded-lg flex justify-between items-center gap-3"><div><div className="font-medium">{job.company_name} - {job.role_title}</div><div className="text-xs text-slate-400 mt-1">Package: {job.package_lpa} LPA | Min CGPA: {job.min_cgpa} | Max Backlogs: {job.max_backlogs}</div>{!job.eligible && <div className="text-xs text-rose-400 mt-1">{job.reason}</div>}</div>{appliedJobIds.has(job.id) ? <span className="text-xs text-slate-400">Already Applied</span> : <button onClick={() => apply(job.id)} disabled={!job.eligible} className="px-4 py-2 bg-indigo-600 disabled:opacity-40 rounded-lg text-white text-sm">Apply</button>}</div>)}{jobs.length===0 && <p className="text-slate-400 text-sm">No job listings available yet.</p>}</div></div>

    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700"><h3 className="font-semibold text-lg mb-4">My Applications</h3><div className="space-y-3">{applications.map(a => <div key={a.id} className="bg-slate-900 p-4 rounded-lg space-y-2"><div className="flex justify-between items-center"><div><div className="font-medium">{a.company_name} - {a.job_title}</div><div className="text-xs text-slate-400">Applied {new Date(a.applied_at).toLocaleDateString()}</div></div><StatusBadge status={a.status}/></div>{a.interview && <div className="text-xs text-slate-400">Interview: {new Date(a.interview.scheduled_at).toLocaleString()} — <StatusBadge status={a.interview.result}/></div>}{a.offer && a.status==='OFFERED' && <div className="flex items-center gap-3 pt-1"><span className="text-xs text-slate-300">Offer: {a.offer.package_lpa} LPA</span><button onClick={() => respondToOffer(a.id,true)} className="px-3 py-1 bg-emerald-700 rounded-md text-xs">Accept</button><button onClick={() => respondToOffer(a.id,false)} className="px-3 py-1 bg-rose-800 rounded-md text-xs">Decline</button></div>}</div>)}{applications.length===0 && <p className="text-slate-400 text-sm">You haven't applied to any jobs yet.</p>}</div></div>
  </div>;
}
