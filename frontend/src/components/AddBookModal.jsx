import React, { useState } from 'react';

export default function AddBookModal({ onClose, onConfirm, isSubmitting }) {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [totalCopies, setTotalCopies] = useState(3);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const cleanTitle = title.trim();
    const cleanAuthor = author.trim();
    const copies = parseInt(totalCopies, 10);

    if (!cleanTitle) {
      setError('Title cannot be empty.');
      return;
    }
    if (!cleanAuthor) {
      setError('Author cannot be empty.');
      return;
    }
    if (isNaN(copies) || copies <= 0) {
      setError('Total copies must be a positive integer greater than 0.');
      return;
    }

    setError('');
    onConfirm({
      title: cleanTitle,
      author: cleanAuthor,
      total_copies: copies,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Add New Book to Catalog</h3>
          <button className="alert-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div className="alert alert-danger" style={{ marginBottom: '1rem', padding: '0.65rem 1rem' }}>
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="book-title">
                Book Title <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <input
                id="book-title"
                type="text"
                className="form-input"
                placeholder="e.g. Distributed Systems Principles and Paradigms"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                autoFocus
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="book-author">
                Author(s) <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <input
                id="book-author"
                type="text"
                className="form-input"
                placeholder="e.g. Andrew S. Tanenbaum, Maarten van Steen"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="book-copies">
                Total Copies in Inventory <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <input
                id="book-copies"
                type="number"
                min="1"
                step="1"
                className="form-input"
                value={totalCopies}
                onChange={(e) => setTotalCopies(e.target.value)}
                disabled={isSubmitting}
              />
              <p className="form-helper">
                Available copies will be initialized to this total number.
              </p>
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
              {isSubmitting ? 'Adding...' : 'Add Book'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
