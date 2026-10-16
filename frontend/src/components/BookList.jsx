import React, { useState } from 'react';

export default function BookList({ books, onReserveClick, isLoading }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'available', 'exhausted'

  const filteredBooks = books.filter((book) => {
    const matchesSearch =
      book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      book.author.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (filterType === 'available') return book.available_copies > 0;
    if (filterType === 'exhausted') return book.available_copies === 0;
    return true;
  });

  return (
    <div>
      {/* Search and Filters Bar */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div style={{ flex: '1', minWidth: '240px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search by book title or author..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className={`btn btn-sm ${filterType === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilterType('all')}
          >
            All ({books.length})
          </button>
          <button
            className={`btn btn-sm ${filterType === 'available' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilterType('available')}
          >
            Available ({books.filter((b) => b.available_copies > 0).length})
          </button>
          <button
            className={`btn btn-sm ${filterType === 'exhausted' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilterType('exhausted')}
          >
            Fully Reserved ({books.filter((b) => b.available_copies === 0).length})
          </button>
        </div>
      </div>

      {/* Book Grid */}
      {isLoading ? (
        <div className="empty-state">
          <div className="empty-icon">⏳</div>
          <div className="empty-title">Loading library catalog...</div>
          <div className="empty-desc">Fetching real-time book availability and processing expirations.</div>
        </div>
      ) : filteredBooks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <div className="empty-title">No books found</div>
          <div className="empty-desc">
            {searchQuery
              ? `No books match "${searchQuery}". Try a different search.`
              : 'No books match the selected filter.'}
          </div>
        </div>
      ) : (
        <div className="books-grid">
          {filteredBooks.map((book) => {
            const isAvailable = book.available_copies > 0;
            const percentAvailable = Math.round((book.available_copies / book.total_copies) * 100);

            let badgeClass = 'badge-success';
            let badgeText = `${book.available_copies} Available`;
            let barColor = 'var(--success)';

            if (book.available_copies === 0) {
              badgeClass = 'badge-danger';
              badgeText = 'Fully Reserved';
              barColor = 'var(--danger)';
            } else if (book.available_copies === 1) {
              badgeClass = 'badge-warning';
              badgeText = '1 Copy Left';
              barColor = 'var(--warning)';
            }

            return (
              <div key={book.id} className="book-card">
                <div>
                  <div className="book-header">
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>
                      ID #{book.id}
                    </span>
                    <span className={`badge ${badgeClass}`}>{badgeText}</span>
                  </div>

                  <h3 className="book-title" title={book.title}>
                    {book.title}
                  </h3>
                  <p className="book-author">by {book.author}</p>
                </div>

                <div>
                  <div className="availability-section">
                    <div className="availability-label">
                      <span>Inventory Ratio</span>
                      <span style={{ fontWeight: 600, color: '#fff' }}>
                        {book.available_copies} of {book.total_copies} copies
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${percentAvailable}%`,
                          backgroundColor: barColor,
                        }}
                      ></div>
                    </div>
                  </div>

                  <button
                    className={`btn ${isAvailable ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ width: '100%' }}
                    onClick={() => onReserveClick(book)}
                    disabled={!isAvailable}
                  >
                    <span>{isAvailable ? '🔖 Reserve a Copy' : '🚫 No Copies Available'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
