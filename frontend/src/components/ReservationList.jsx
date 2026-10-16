import React, { useState } from 'react';

export default function ReservationList({ reservations, onCancelReservation, isCancellingId, isLoading }) {
  const [statusFilter, setStatusFilter] = useState('all'); // 'all', 'active', 'cancelled', 'expired'

  const filteredReservations = reservations.filter((r) => {
    if (statusFilter === 'all') return true;
    return r.status === statusFilter;
  });

  const formatDate = (isoString) => {
    if (!isoString) return '—';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  const getExpirationDisplay = (res) => {
    const formatted = formatDate(res.expires_at);
    if (res.status === 'expired') {
      return <span style={{ color: 'var(--danger)' }}>{formatted} (Expired)</span>;
    }
    if (res.status === 'cancelled') {
      return <span style={{ color: 'var(--text-dim)' }}>{formatted}</span>;
    }

    // Active
    const now = new Date();
    const exp = new Date(res.expires_at);
    const diffHours = Math.round((exp - now) / (1000 * 60 * 60));

    if (diffHours <= 0) {
      return <span style={{ color: 'var(--danger)' }}>Pending Expiration</span>;
    }
    if (diffHours < 24) {
      return <span style={{ color: 'var(--warning)' }}>{formatted} ({diffHours}h left)</span>;
    }
    const days = Math.round(diffHours / 24);
    return <span style={{ color: '#a5b4fc' }}>{formatted} ({days}d left)</span>;
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <span className="badge badge-active">Active</span>;
      case 'cancelled':
        return <span className="badge badge-neutral">Cancelled</span>;
      case 'expired':
        return <span className="badge badge-danger">Expired</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  return (
    <div>
      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button
          className={`btn btn-sm ${statusFilter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setStatusFilter('all')}
        >
          All ({reservations.length})
        </button>
        <button
          className={`btn btn-sm ${statusFilter === 'active' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setStatusFilter('active')}
        >
          Active ({reservations.filter((r) => r.status === 'active').length})
        </button>
        <button
          className={`btn btn-sm ${statusFilter === 'cancelled' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setStatusFilter('cancelled')}
        >
          Cancelled ({reservations.filter((r) => r.status === 'cancelled').length})
        </button>
        <button
          className={`btn btn-sm ${statusFilter === 'expired' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setStatusFilter('expired')}
        >
          Expired ({reservations.filter((r) => r.status === 'expired').length})
        </button>
      </div>

      {isLoading ? (
        <div className="empty-state">
          <div className="empty-icon">⏳</div>
          <div className="empty-title">Loading reservations...</div>
        </div>
      ) : filteredReservations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <div className="empty-title">No reservations found</div>
          <div className="empty-desc">
            {statusFilter === 'all'
              ? 'No books have been reserved yet. Select a book from the catalog to reserve a copy!'
              : `No reservations with status "${statusFilter}".`}
          </div>
        </div>
      ) : (
        <div className="reservations-table-wrapper">
          <table className="reservations-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Book Title</th>
                <th>User</th>
                <th>Reserved Date</th>
                <th>Expires At</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredReservations.map((res) => (
                <tr key={res.id}>
                  <td style={{ fontWeight: 600, color: 'var(--text-dim)' }}>#{res.id}</td>
                  <td>
                    <div style={{ fontWeight: 600, color: '#fff' }}>
                      {res.book_title || `Book #${res.book_id}`}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                      Book ID: {res.book_id}
                    </div>
                  </td>
                  <td>
                    <span style={{ fontWeight: 500, color: '#e0e7ff' }}>
                      👤 {res.user_name}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{formatDate(res.reservation_date)}</td>
                  <td>{getExpirationDisplay(res)}</td>
                  <td>{getStatusBadge(res.status)}</td>
                  <td style={{ textAlign: 'right' }}>
                    {res.status === 'active' ? (
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => onCancelReservation(res.id)}
                        disabled={isCancellingId === res.id}
                        title="Cancel reservation and return 1 copy to inventory"
                      >
                        {isCancellingId === res.id ? 'Cancelling...' : 'Cancel Reservation'}
                      </button>
                    ) : (
                      <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                        {res.status === 'cancelled' ? 'Freed by User' : 'Auto-Freed'}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
