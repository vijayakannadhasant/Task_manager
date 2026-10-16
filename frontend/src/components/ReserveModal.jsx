import React, { useState } from 'react';

export default function ReserveModal({ book, onClose, onConfirm, isSubmitting }) {
  const [userName, setUserName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = userName.trim();
    if (!trimmed) {
      setError('Please enter your name or username.');
      return;
    }
    setError('');
    onConfirm(book.id, trimmed);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Reserve Book Copy</h3>
          <button className="alert-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div style={{ marginBottom: '1.25rem', padding: '1rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)' }}>
              <h4 style={{ fontSize: '1.05rem', color: '#fff', marginBottom: '0.25rem' }}>{book.title}</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>by {book.author}</p>
              <div style={{ marginTop: '0.75rem', fontSize: '0.82rem', color: 'var(--success)' }}>
                ✔ {book.available_copies} of {book.total_copies} copies currently available
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="res-username">
                Your Full Name / Username <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <input
                id="res-username"
                type="text"
                className="form-input"
                placeholder="e.g. alex_chen or Alice Smith"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                autoFocus
                disabled={isSubmitting}
              />
              <p className="form-helper">
                This name will be attached to the reservation record.
              </p>
              {error && (
                <p style={{ color: 'var(--danger)', fontSize: '0.82rem', marginTop: '0.35rem' }}>
                  {error}
                </p>
              )}
            </div>

            <div style={{ padding: '0.75rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(99, 102, 241, 0.2)', fontSize: '0.82rem', color: '#c7d2fe' }}>
              ℹ️ <strong>Reservation Policy:</strong> Each reservation holds 1 physical copy for exactly <strong>7 days</strong>. If not renewed or collected, it automatically expires and frees the copy back to inventory.
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Confirming...' : 'Confirm Reservation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
