import React, { useState } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';

interface BudgetConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  currentLimit?: number;
}

const BudgetConfigModal: React.FC<BudgetConfigModalProps> = ({ 
  isOpen, 
  onClose, 
  onSave, 
  currentLimit = 0
}) => {
  const [amount, setAmount] = useState<string>(currentLimit ? currentLimit.toString() : '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const value = parseFloat(amount);
      if (isNaN(value) || value <= 0) {
        throw new Error("Please enter a valid positive amount");
      }

      const response = await fetch(`${apiUrl}/budgets/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: value })
      });

      if (!response.ok) {
        throw new Error("Failed to save budget configuration");
      }

      onSave(); // Refresh parent
      onClose();
    } catch (err) {
        const msg = err instanceof Error ? err.message : "An error occurred";
        setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md border border-slate-200">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-800">Set Monthly Budget</h3>
          <button 
            onClick={onClose}
            className="p-1 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Monthly Limit (USD)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-medium">$</span>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="50.00"
                className="w-full pl-8 pr-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                autoFocus
              />
            </div>
            <p className="text-xs text-slate-500">
              We will alert you when your monthly spend reaches 80% and 100% of this limit.
            </p>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Footer */}
          <div className="pt-2 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-50 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              Save Budget
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BudgetConfigModal;
