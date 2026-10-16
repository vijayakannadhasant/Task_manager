import React from 'react';

export default function StatsOverview({ books, reservations }) {
  const totalBooks = books.length;
  const totalAvailable = books.reduce((acc, b) => acc + b.available_copies, 0);
  const totalCopies = books.reduce((acc, b) => acc + b.total_copies, 0);
  const activeReservations = reservations.filter((r) => r.status === 'active').length;
  const outOfStockBooks = books.filter((b) => b.available_copies === 0).length;

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
          📖
        </div>
        <div className="stat-info">
          <h4>Catalog Titles</h4>
          <div className="stat-value">{totalBooks}</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
          ✨
        </div>
        <div className="stat-info">
          <h4>Available Copies</h4>
          <div className="stat-value">
            {totalAvailable} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {totalCopies}</span>
          </div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee' }}>
          🔖
        </div>
        <div className="stat-info">
          <h4>Active Reservations</h4>
          <div className="stat-value">{activeReservations}</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
          ⚠️
        </div>
        <div className="stat-info">
          <h4>Fully Reserved</h4>
          <div className="stat-value">{outOfStockBooks}</div>
        </div>
      </div>
    </div>
  );
}
