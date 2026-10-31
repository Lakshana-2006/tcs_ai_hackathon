import React, { useState, useEffect } from 'react';
import { 
  Star, 
  Send, 
  RotateCcw, 
  CheckCircle2, 
  AlertCircle, 
  MessageSquarePlus, 
  BarChart3, 
  UserCheck, 
  Sparkles, 
  Loader2, 
  Clock, 
  Award, 
  ShieldCheck,
  TrendingUp,
  MessageCircle,
  HelpCircle,
  Users
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  Cell 
} from 'recharts';
import { submitFeedback, fetchFeedbackSummary, fetchFeedbackList } from '../api';

const ROLES = [
  { id: 'Judge', label: 'Judge / Evaluator', icon: Award },
  { id: 'Evaluator', label: 'Technical Evaluator', icon: ShieldCheck },
  { id: 'Faculty', label: 'Academic Faculty / Researcher', icon: UserCheck },
  { id: 'Student', label: 'Student / Developer', icon: Users },
  { id: 'Other', label: 'Urban Planner / Public User', icon: MessageCircle }
];

const RATING_CATEGORIES = [
  { id: 'overall_rating', label: 'Overall System Rating', desc: 'Overall platform effectiveness, architecture & presentation' },
  { id: 'ease_of_use', label: 'Ease of Use & UX', desc: 'Interface navigation, city search & responsiveness' },
  { id: 'data_visualization', label: 'Data Visualization & Cartography', desc: 'Leaflet raster overlays, charts & KPI metric cards' },
  { id: 'heat_risk_analysis', label: 'Heat Risk Modeling & Science', desc: 'IPCC formula fidelity, past/present/future analysis & GEE' },
  { id: 'intervention_recommendations', label: 'Interventions & Optimizer', desc: 'Simulation accuracy, budget optimizer & biophysical rules' }
];

const RATING_LABELS = {
  1: '1 - Needs Improvement',
  2: '2 - Fair',
  3: '3 - Good',
  4: '4 - Very Good',
  5: '5 - Outstanding'
};

function StarRating({ value, onChange, label, desc, error }) {
  const [hoverVal, setHoverVal] = useState(0);

  return (
    <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800 space-y-1.5 transition hover:border-slate-700">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <div>
          <span className="text-xs font-semibold text-slate-200">{label}</span>
          {desc && <p className="text-[10px] text-slate-400">{desc}</p>}
        </div>
        <div className="text-[11px] font-mono font-medium text-amber-400 h-4">
          {RATING_LABELS[hoverVal || value] || 'Select rating (1-5★)'}
        </div>
      </div>

      <div className="flex items-center gap-1.5 pt-0.5">
        {[1, 2, 3, 4, 5].map((star) => {
          const filled = (hoverVal || value) >= star;
          return (
            <button
              key={star}
              type="button"
              onClick={() => onChange(star)}
              onMouseEnter={() => setHoverVal(star)}
              onMouseLeave={() => setHoverVal(0)}
              className="p-1 rounded-md hover:bg-slate-800/80 transition-transform active:scale-90 focus:outline-none focus:ring-1 focus:ring-amber-400"
              title={`${star} Star${star > 1 ? 's' : ''}`}
            >
              <Star
                className={`w-5 h-5 transition-colors ${
                  filled 
                    ? 'text-amber-400 fill-amber-400 drop-shadow-[0_0_6px_rgba(251,191,36,0.5)]' 
                    : 'text-slate-600 hover:text-slate-400'
                }`}
              />
            </button>
          );
        })}
      </div>

      {error && <p className="text-[10px] text-rose-400 font-medium">{error}</p>}
    </div>
  );
}

export default function FeedbackSession({ activeCity }) {
  // Form State
  const initialFormState = {
    name: '',
    role: 'Judge',
    overall_rating: 0,
    ease_of_use: 0,
    data_visualization: 0,
    heat_risk_analysis: 0,
    intervention_recommendations: 0,
    most_useful_feature: '',
    suggestions: '',
    additional_comments: ''
  };

  const [formData, setFormData] = useState(initialFormState);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [successResult, setSuccessResult] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  // Summary and Review Feed State
  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [recentList, setRecentList] = useState([]);
  const [loadingList, setLoadingList] = useState(false);
  const [activeView, setActiveView] = useState('form'); // 'form', 'summary', 'reviews'

  // Load Summary
  const refreshData = async () => {
    try {
      setLoadingSummary(true);
      const [sumData, listData] = await Promise.all([
        fetchFeedbackSummary(),
        fetchFeedbackList(15, 0)
      ]);
      setSummary(sumData);
      setRecentList(listData);
    } catch (err) {
      console.warn('Could not load feedback summary:', err.message);
    } finally {
      setLoadingSummary(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  // Validation
  const validate = () => {
    const errs = {};
    if (!formData.role) errs.role = 'Please select your evaluation role.';
    
    if (!formData.overall_rating) errs.overall_rating = 'Please rate the overall system.';
    if (!formData.ease_of_use) errs.ease_of_use = 'Please rate ease of use & UX.';
    if (!formData.data_visualization) errs.data_visualization = 'Please rate data visualization.';
    if (!formData.heat_risk_analysis) errs.heat_risk_analysis = 'Please rate heat risk modeling.';
    if (!formData.intervention_recommendations) errs.intervention_recommendations = 'Please rate interventions.';

    if (!formData.most_useful_feature || formData.most_useful_feature.trim().length < 2) {
      errs.most_useful_feature = 'Please specify the most useful feature (min 2 characters).';
    }
    if (!formData.suggestions || formData.suggestions.trim().length < 3) {
      errs.suggestions = 'Please provide constructive suggestions for improvement (min 3 characters).';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);
    setSuccessResult(null);

    if (!validate()) {
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        name: formData.name.trim() || undefined,
        role: formData.role,
        overall_rating: Number(formData.overall_rating),
        ease_of_use: Number(formData.ease_of_use),
        data_visualization: Number(formData.data_visualization),
        heat_risk_analysis: Number(formData.heat_risk_analysis),
        intervention_recommendations: Number(formData.intervention_recommendations),
        most_useful_feature: formData.most_useful_feature.trim(),
        suggestions: formData.suggestions.trim(),
        additional_comments: formData.additional_comments.trim() || undefined
      };

      const result = await submitFeedback(payload);
      setSuccessResult(result);
      setFormData(initialFormState);
      setErrors({});
      // Refresh summary
      await refreshData();
    } catch (err) {
      setSubmitError(err.message || 'Failed to submit feedback. Please check connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setFormData(initialFormState);
    setErrors({});
    setSubmitError(null);
    setSuccessResult(null);
  };

  // Star Distribution Bar Data
  const ratingDistData = summary?.rating_distribution
    ? Object.keys(summary.rating_distribution).map((stars) => ({
        stars: `${stars} ★`,
        count: summary.rating_distribution[stars]
      }))
    : [];

  const radarData = summary?.category_averages || [];

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="glass-panel rounded-xl p-4 sm:p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border border-amber-500/20 bg-gradient-to-r from-slate-950 via-slate-900 to-amber-950/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center shrink-0">
            <MessageSquarePlus className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>HEATSHIELD AI — Hackathon Evaluator & Judge Feedback Session</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">
                Persistent Storage
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Submit structured ratings, feature evaluations, and suggestions for urban resilience decision-support.
            </p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center gap-1.5 bg-slate-950/80 p-1 rounded-lg border border-slate-800 shrink-0 self-stretch sm:self-auto justify-center">
          <button
            onClick={() => setActiveView('form')}
            className={`text-xs px-3 py-1.5 rounded-md font-semibold transition flex items-center gap-1.5 ${
              activeView === 'form'
                ? 'bg-amber-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <MessageSquarePlus className="w-3.5 h-3.5" />
            <span>Submit Feedback</span>
          </button>

          <button
            onClick={() => setActiveView('summary')}
            className={`text-xs px-3 py-1.5 rounded-md font-semibold transition flex items-center gap-1.5 ${
              activeView === 'summary'
                ? 'bg-cyan-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Aggregate Analytics ({summary?.total_submissions || 0})</span>
          </button>

          <button
            onClick={() => setActiveView('reviews')}
            className={`text-xs px-3 py-1.5 rounded-md font-semibold transition flex items-center gap-1.5 ${
              activeView === 'reviews'
                ? 'bg-purple-500 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Recent Feed</span>
          </button>
        </div>
      </div>

      {/* VIEW 1: FEEDBACK SUBMISSION FORM */}
      {activeView === 'form' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Main Form Column */}
          <div className="lg:col-span-8 glass-panel rounded-xl p-4 sm:p-6 space-y-5">
            {/* Success Message Banner */}
            {successResult && (
              <div className="bg-emerald-950/70 border border-emerald-500/40 rounded-xl p-4 text-emerald-300 space-y-1.5 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-1 text-xs">
                  <p className="font-bold text-sm text-white">Thank you! Your feedback has been recorded persistently.</p>
                  <p className="text-slate-300">
                    Submission ID: <code className="text-emerald-400 font-mono text-[11px]">{successResult.id}</code> • Recorded at {successResult.created_at}.
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Your evaluation scores have been incorporated into the aggregate analytics.
                  </p>
                </div>
              </div>
            )}

            {/* Error Message Banner */}
            {submitError && (
              <div className="bg-rose-950/60 border border-rose-500/40 rounded-xl p-3.5 text-rose-300 flex items-center gap-2.5 text-xs">
                <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
                <div>
                  <span className="font-bold">Submission Failed: </span>
                  <span>{submitError}</span>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Identity & Role Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <span>Your Name / Affiliation</span>
                    <span className="text-[10px] text-slate-500 font-normal">Optional</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Dr. Jane Smith, IIT Madras"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-amber-500 rounded-lg px-3 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <span>Evaluation Role <strong className="text-rose-400">*</strong></span>
                    <span className="text-[10px] text-amber-400 font-mono">Required</span>
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-amber-500 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer"
                  >
                    {ROLES.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 5-Star Rating Grid */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                    <Star className="w-3.5 h-3.5 text-amber-400" />
                    <span>Evaluation Dimensions (1 to 5 Stars)</span>
                  </span>
                  <span className="text-[10px] text-slate-400">All 5 dimensions required</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {RATING_CATEGORIES.map((cat) => (
                    <StarRating
                      key={cat.id}
                      label={cat.label}
                      desc={cat.desc}
                      value={formData[cat.id]}
                      onChange={(val) => {
                        setFormData((prev) => ({ ...prev, [cat.id]: val }));
                        if (errors[cat.id]) {
                          setErrors((prev) => {
                            const updated = { ...prev };
                            delete updated[cat.id];
                            return updated;
                          });
                        }
                      }}
                      error={errors[cat.id]}
                    />
                  ))}
                </div>
              </div>

              {/* Qualitative Text Questions */}
              <div className="space-y-3.5">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <span>Which feature did you find most useful or innovative? <strong className="text-rose-400">*</strong></span>
                    <span className="text-[10px] text-slate-500">Required</span>
                  </label>
                  <input
                    type="text"
                    value={formData.most_useful_feature}
                    onChange={(e) => {
                      setFormData({ ...formData, most_useful_feature: e.target.value });
                      if (errors.most_useful_feature) {
                        setErrors((prev) => {
                          const n = { ...prev };
                          delete n.most_useful_feature;
                          return n;
                        });
                      }
                    }}
                    placeholder="e.g., Landsat ST_B10 thermal conversion, budget optimizer knapsack, or multi-horizon climate comparison..."
                    className={`w-full bg-slate-950 border rounded-lg px-3 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 ${
                      errors.most_useful_feature ? 'border-rose-500 focus:ring-rose-500' : 'border-slate-800 focus:border-amber-500 focus:ring-amber-500'
                    }`}
                  />
                  {errors.most_useful_feature && (
                    <p className="text-[10px] text-rose-400 font-medium">{errors.most_useful_feature}</p>
                  )}
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <span>Constructive Suggestions for Improvement <strong className="text-rose-400">*</strong></span>
                    <span className="text-[10px] text-slate-500">Required</span>
                  </label>
                  <textarea
                    rows={3}
                    value={formData.suggestions}
                    onChange={(e) => {
                      setFormData({ ...formData, suggestions: e.target.value });
                      if (errors.suggestions) {
                        setErrors((prev) => {
                          const n = { ...prev };
                          delete n.suggestions;
                          return n;
                        });
                      }
                    }}
                    placeholder="e.g., What additional datasets, policy constraints, or UI controls would make this platform more viable for city municipal engineers?"
                    className={`w-full bg-slate-950 border rounded-lg px-3 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 resize-y ${
                      errors.suggestions ? 'border-rose-500 focus:ring-rose-500' : 'border-slate-800 focus:border-amber-500 focus:ring-amber-500'
                    }`}
                  />
                  {errors.suggestions && (
                    <p className="text-[10px] text-rose-400 font-medium">{errors.suggestions}</p>
                  )}
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <span>Additional Evaluation Comments / Feedback</span>
                    <span className="text-[10px] text-slate-500">Optional</span>
                  </label>
                  <textarea
                    rows={2}
                    value={formData.additional_comments}
                    onChange={(e) => setFormData({ ...formData, additional_comments: e.target.value })}
                    placeholder="Any general thoughts, hackathon remarks, or praise..."
                    className="w-full bg-slate-950 border border-slate-800 focus:border-amber-500 rounded-lg px-3 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-amber-500 resize-y"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={handleReset}
                  disabled={submitting}
                  className="text-xs px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1.5 disabled:opacity-50"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset Form</span>
                </button>

                <button
                  type="submit"
                  disabled={submitting}
                  className="text-xs font-bold px-6 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 shadow-lg shadow-amber-500/20 transition flex items-center gap-2 disabled:opacity-50"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                      <span>Saving Feedback...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>Submit Evaluation</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Quick Summary Side Card */}
          <div className="lg:col-span-4 space-y-4">
            <div className="glass-panel rounded-xl p-4 sm:p-5 space-y-4 border border-slate-800">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-amber-400" />
                  <span>Live Evaluation Metrics</span>
                </span>
                <span className="text-[10px] font-mono text-cyan-400">
                  {summary?.total_submissions || 0} Submissions
                </span>
              </div>

              {/* Big Score Card */}
              <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 text-center space-y-1">
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Average Overall Score</div>
                <div className="text-3xl font-black text-amber-400 font-mono flex items-center justify-center gap-1">
                  <span>{summary?.avg_overall_rating ? summary.avg_overall_rating.toFixed(2) : '—'}</span>
                  <span className="text-xs text-slate-500 font-normal">/ 5.0</span>
                </div>
                <div className="flex items-center justify-center gap-1 text-amber-400">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <Star
                      key={s}
                      className={`w-3.5 h-3.5 ${
                        (summary?.avg_overall_rating || 0) >= s
                          ? 'fill-amber-400'
                          : 'text-slate-600'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* Dimension Averages List */}
              <div className="space-y-2 text-xs">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Dimension Averages</span>
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                    <span className="text-slate-300">Ease of Use & UX</span>
                    <span className="font-mono font-bold text-cyan-300">
                      {summary?.avg_ease_of_use ? `${summary.avg_ease_of_use.toFixed(1)} ★` : '—'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                    <span className="text-slate-300">Data Visualization</span>
                    <span className="font-mono font-bold text-purple-300">
                      {summary?.avg_data_visualization ? `${summary.avg_data_visualization.toFixed(1)} ★` : '—'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                    <span className="text-slate-300">Heat Risk Modeling</span>
                    <span className="font-mono font-bold text-rose-300">
                      {summary?.avg_heat_risk_analysis ? `${summary.avg_heat_risk_analysis.toFixed(1)} ★` : '—'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                    <span className="text-slate-300">Intervention Recommendations</span>
                    <span className="font-mono font-bold text-emerald-300">
                      {summary?.avg_intervention_recommendations ? `${summary.avg_intervention_recommendations.toFixed(1)} ★` : '—'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Evaluator Guidelines Note */}
              <div className="text-[11px] text-slate-400 bg-slate-950/70 p-3 rounded-lg border border-slate-800/80 space-y-1">
                <span className="font-bold text-slate-300 flex items-center gap-1">
                  <HelpCircle className="w-3 h-3 text-cyan-400" /> Hackathon Evaluation Focus
                </span>
                <p className="leading-relaxed">
                  Your feedback validates the digital twin's scientific integrity, real-time Open-Meteo weather telemetry, Landsat 8/9 thermal calibration, and IPCC decision-support usability.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: AGGREGATE SUMMARY & RECHARTS ANALYTICS */}
      {activeView === 'summary' && (
        <div className="space-y-4">
          {loadingSummary ? (
            <div className="glass-panel rounded-xl p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
              <Loader2 className="w-6 h-6 animate-spin text-amber-400" />
              <p className="text-xs">Computing aggregate rating distributions...</p>
            </div>
          ) : !summary || summary.total_submissions === 0 ? (
            <div className="glass-panel rounded-xl p-12 text-center space-y-3">
              <MessageSquarePlus className="w-10 h-10 text-slate-600 mx-auto" />
              <h3 className="font-bold text-white text-base">No Feedback Submissions Yet</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Be the first judge, evaluator, or student to submit an evaluation! Ratings and feedback are stored persistently in SQLite.
              </p>
              <button
                onClick={() => setActiveView('form')}
                className="mt-2 text-xs font-semibold px-4 py-2 rounded-lg bg-amber-500 text-slate-950 hover:bg-amber-400 transition"
              >
                Open Evaluation Form
              </button>
            </div>
          ) : (
            <>
              {/* 5 KPI Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="glass-panel rounded-xl p-3 border border-slate-800 text-center">
                  <div className="text-[10px] text-slate-400 font-semibold uppercase">Total Reviews</div>
                  <div className="text-2xl font-bold font-mono text-white mt-1">{summary.total_submissions}</div>
                  <div className="text-[9px] text-slate-500">Persistent Records</div>
                </div>

                <div className="glass-panel rounded-xl p-3 border border-amber-500/30 text-center bg-amber-500/5">
                  <div className="text-[10px] text-amber-300 font-semibold uppercase">Overall Rating</div>
                  <div className="text-2xl font-bold font-mono text-amber-400 mt-1">{summary.avg_overall_rating} ★</div>
                  <div className="text-[9px] text-slate-400">Mean 5-Star Scale</div>
                </div>

                <div className="glass-panel rounded-xl p-3 border border-cyan-500/30 text-center bg-cyan-500/5">
                  <div className="text-[10px] text-cyan-300 font-semibold uppercase">Ease of Use</div>
                  <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">{summary.avg_ease_of_use} ★</div>
                  <div className="text-[9px] text-slate-400">UX & Flow</div>
                </div>

                <div className="glass-panel rounded-xl p-3 border border-purple-500/30 text-center bg-purple-500/5">
                  <div className="text-[10px] text-purple-300 font-semibold uppercase">Data Visualization</div>
                  <div className="text-2xl font-bold font-mono text-purple-400 mt-1">{summary.avg_data_visualization} ★</div>
                  <div className="text-[9px] text-slate-400">Cartography & Charts</div>
                </div>

                <div className="glass-panel rounded-xl p-3 border border-rose-500/30 text-center bg-rose-500/5">
                  <div className="text-[10px] text-rose-300 font-semibold uppercase">Risk Modeling</div>
                  <div className="text-2xl font-bold font-mono text-rose-400 mt-1">{summary.avg_heat_risk_analysis} ★</div>
                  <div className="text-[9px] text-slate-400">IPCC AR6 Formula</div>
                </div>

                <div className="glass-panel rounded-xl p-3 border border-emerald-500/30 text-center bg-emerald-500/5">
                  <div className="text-[10px] text-emerald-300 font-semibold uppercase">Interventions</div>
                  <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">{summary.avg_intervention_recommendations} ★</div>
                  <div className="text-[9px] text-slate-400">Policy Recommendations</div>
                </div>
              </div>

              {/* Recharts Visualizations Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                {/* 1. Radar Chart: 5 Evaluation Dimensions */}
                <div className="lg:col-span-6 glass-panel rounded-xl p-4 sm:p-5 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <TrendingUp className="w-4 h-4 text-cyan-400" />
                      <span>Dimensional Competency Profile (Radar Assessment)</span>
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">Max: 5.0</span>
                  </div>

                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                        <PolarGrid stroke="#334155" />
                        <PolarAngleAxis dataKey="category" stroke="#94a3b8" tick={{ fill: '#cbd5e1', fontSize: 10 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 5]} stroke="#475569" />
                        <Radar name="Score" dataKey="score" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.35} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                          formatter={(val) => [`${val} / 5.0`, 'Rating']}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* 2. Star Distribution Bar Chart */}
                <div className="lg:col-span-6 glass-panel rounded-xl p-4 sm:p-5 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <Star className="w-4 h-4 text-amber-400" />
                      <span>Star Rating Distribution (Overall System)</span>
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">Total: {summary.total_submissions}</span>
                  </div>

                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={ratingDistData} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 10 }}>
                        <XAxis type="number" allowDecimals={false} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                        <YAxis dataKey="stars" type="category" stroke="#64748b" tick={{ fill: '#fbbf24', fontSize: 11, fontWeight: 'bold' }} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                          formatter={(count) => [`${count} submission(s)`, 'Count']}
                        />
                        <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                          {ratingDistData.map((entry, index) => {
                            const colors = ['#f43f5e', '#fb923c', '#fbbf24', '#38bdf8', '#34d399'];
                            return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                          })}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Role Breakdown Row */}
              <div className="glass-panel rounded-xl p-4 border border-slate-800 space-y-2">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Submissions by Role</span>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                  {Object.keys(summary.role_breakdown || {}).map((role) => (
                    <div key={role} className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/80 text-center">
                      <div className="text-[10px] text-slate-400">{role}</div>
                      <div className="text-lg font-bold font-mono text-white mt-0.5">{summary.role_breakdown[role]}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* VIEW 3: RECENT FEED */}
      {activeView === 'reviews' && (
        <div className="glass-panel rounded-xl p-4 sm:p-6 space-y-4 border border-slate-800">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-bold text-white flex items-center gap-1.5">
              <Users className="w-4 h-4 text-purple-400" />
              <span>Recent Feedback Submissions (Reverse Chronological)</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Showing {recentList.length} of {summary?.total_submissions || recentList.length}
            </span>
          </div>

          {recentList.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs">
              No feedback records found. Submit feedback to see it listed here.
            </div>
          ) : (
            <div className="space-y-3">
              {recentList.map((item) => (
                <div key={item.id} className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80 space-y-2 text-xs">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-slate-900 pb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white">{item.name || 'Anonymous Evaluator'}</span>
                      <span className="text-[9px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                        {item.role}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] font-mono">
                      <div className="flex items-center gap-1 text-amber-400">
                        <Star className="w-3.5 h-3.5 fill-amber-400" />
                        <span className="font-bold">{item.overall_rating}.0 / 5.0</span>
                      </div>
                      <span className="text-slate-500 text-[10px] flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {item.created_at}
                      </span>
                    </div>
                  </div>

                  {/* Dimensions Strip */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 text-[10px] font-mono text-slate-400">
                    <div className="bg-slate-900/60 p-1 rounded px-2">Ease: <strong className="text-cyan-300">{item.ease_of_use}★</strong></div>
                    <div className="bg-slate-900/60 p-1 rounded px-2">Data Viz: <strong className="text-purple-300">{item.data_visualization}★</strong></div>
                    <div className="bg-slate-900/60 p-1 rounded px-2">Risk Model: <strong className="text-rose-300">{item.heat_risk_analysis}★</strong></div>
                    <div className="bg-slate-900/60 p-1 rounded px-2">Interventions: <strong className="text-emerald-300">{item.intervention_recommendations}★</strong></div>
                  </div>

                  {/* Most useful feature */}
                  <div className="text-[11px] text-slate-300">
                    <span className="text-slate-500 font-semibold">Most Useful: </span>
                    <span className="italic text-cyan-300">"{item.most_useful_feature}"</span>
                  </div>

                  {/* Suggestions */}
                  <div className="text-[11px] text-slate-300">
                    <span className="text-slate-500 font-semibold">Suggestions: </span>
                    <span>{item.suggestions}</span>
                  </div>

                  {/* Comments */}
                  {item.additional_comments && (
                    <div className="text-[10px] text-slate-400 bg-slate-900/40 p-2 rounded border border-slate-900">
                      <span className="text-slate-500 font-semibold">Remarks: </span>
                      <span>{item.additional_comments}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

