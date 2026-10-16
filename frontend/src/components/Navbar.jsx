import React from 'react';

export default function Navbar({ onAddBookClick, onRefreshClick, isRefreshing, autoSync, setAutoSync }) {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">📚</div>
        <div>
          <h1 className="brand-title">Library Reservation System</h1>
          <p className="brand-subtitle">Inventory Management, 7-Day Reservations & Expiration Tracking</p>
        </div>
      </div>

      <div className="nav-actions">
        <div
          className="live-indicator"
          style={{ cursor: 'pointer' }}
          onClick={() => setAutoSync(!autoSync)}
          title="Click to toggle lightweight auto-sync polling"
        >
          <span className="pulse-dot" style={{ backgroundColor: autoSync ? 'var(--success)' : 'var(--text-dim)' }}></span>
          <span>{autoSync ? 'Auto-Sync (8s)' : 'Sync Paused'}</span>
        </div>

        <button
          className="btn btn-secondary btn-sm"
          onClick={onRefreshClick}
          disabled={isRefreshing}
          title="Manually refresh book availability and process expirations"
        >
          <span>🔄</span>
          <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
        </button>

        <button className="btn btn-primary btn-sm" onClick={onAddBookClick}>
          <span>➕</span>
          <span>Add Book</span>
        </button>
      </div>
    </header>
  );
}
