import React, { useState, useEffect, useCallback, useRef } from 'react';
import Navbar from './components/Navbar';
import StatsOverview from './components/StatsOverview';
import BookList from './components/BookList';
import ReservationList from './components/ReservationList';
import ReserveModal from './components/ReserveModal';
import AddBookModal from './components/AddBookModal';
import {
  fetchBooks,
  fetchReservations,
  createBook,
  reserveBook,
  cancelReservation,
  getErrorMessage,
} from './api/client';

export default function App() {
  const [books, setBooks] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [activeTab, setActiveTab] = useState('books'); // 'books' or 'reservations'
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCancellingId, setIsCancellingId] = useState(null);
  const [alert, setAlert] = useState(null);

  // Modals state
  const [selectedBookForReserve, setSelectedBookForReserve] = useState(null);
  const [isAddBookOpen, setIsAddBookOpen] = useState(false);

  // Bonus Real-time sync
  const [autoSync, setAutoSync] = useState(true);
  const isMountedRef = useRef(true);

  const loadData = useCallback(async (silent = false) => {
    if (!silent) setIsRefreshing(true);
    try {
      const [booksData, reservationsData] = await Promise.all([
        fetchBooks(),
        fetchReservations(),
      ]);
      if (isMountedRef.current) {
        setBooks(booksData);
        setReservations(reservationsData);
      }
    } catch (err) {
      if (!silent && isMountedRef.current) {
        setAlert({
          type: 'danger',
          message: `Connection Error: ${getErrorMessage(err)}. Is the backend running?`,
        });
      }
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    }
  }, []);

  // Initial load
  useEffect(() => {
    isMountedRef.current = true;
    loadData(false);
    return () => {
      isMountedRef.current = false;
    };
  }, [loadData]);

  // Polling for real-time updates
  useEffect(() => {
    if (!autoSync) return;
    const interval = setInterval(() => {
      loadData(true);
    }, 8000);
    return () => clearInterval(interval);
  }, [autoSync, loadData]);

  // Actions
  const handleAddBook = async (bookData) => {
    setIsSubmitting(true);
    try {
      const created = await createBook(bookData);
      setAlert({
        type: 'success',
        message: `Successfully added "${created.title}" with ${created.total_copies} available copies!`,
      });
      setIsAddBookOpen(false);
      await loadData(false);
    } catch (err) {
      setAlert({
        type: 'danger',
        message: `Failed to add book: ${getErrorMessage(err)}`,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReserveBook = async (bookId, userName) => {
    setIsSubmitting(true);
    try {
      const res = await reserveBook(bookId, userName);
      const bookTitle = selectedBookForReserve ? selectedBookForReserve.title : `Book #${bookId}`;
      setAlert({
        type: 'success',
        message: `Reservation confirmed for "${userName}" on "${bookTitle}"! Expires in 7 days.`,
      });
      setSelectedBookForReserve(null);
      await loadData(false);
    } catch (err) {
      setAlert({
        type: 'danger',
        message: `Reservation failed: ${getErrorMessage(err)}`,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelReservation = async (reservationId) => {
    setIsCancellingId(reservationId);
    try {
      const cancelled = await cancelReservation(reservationId);
      setAlert({
        type: 'success',
        message: `Reservation #${cancelled.id} successfully cancelled. Exactly 1 copy restored to inventory!`,
      });
      await loadData(false);
    } catch (err) {
      setAlert({
        type: 'danger',
        message: `Cancellation failed: ${getErrorMessage(err)}`,
      });
    } finally {
      setIsCancellingId(null);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <Navbar
        onAddBookClick={() => setIsAddBookOpen(true)}
        onRefreshClick={() => loadData(false)}
        isRefreshing={isRefreshing}
        autoSync={autoSync}
        setAutoSync={setAutoSync}
      />

      {/* Alert Notification Banner */}
      {alert && (
        <div className={`alert alert-${alert.type}`}>
          <span>{alert.message}</span>
          <button className="alert-close" onClick={() => setAlert(null)}>
            ✕
          </button>
        </div>
      )}

      {/* Overview Cards */}
      <StatsOverview books={books} reservations={reservations} />

      {/* View Switcher Tabs */}
      <div className="tabs-container">
        <div className="nav-tabs">
          <button
            className={`tab-btn ${activeTab === 'books' ? 'active' : ''}`}
            onClick={() => setActiveTab('books')}
          >
            <span>📚 Catalog & Inventory</span>
            <span className="tab-count">{books.length}</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'reservations' ? 'active' : ''}`}
            onClick={() => setActiveTab('reservations')}
          >
            <span>🔖 Reservations</span>
            <span className="tab-count">
              {reservations.filter((r) => r.status === 'active').length} active
            </span>
          </button>
        </div>

        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {activeTab === 'books'
            ? 'Real-time copy availability tracked automatically'
            : 'Automated 7-day expiration enforcement'}
        </div>
      </div>

      {/* Tab Panels */}
      {activeTab === 'books' ? (
        <BookList
          books={books}
          isLoading={isLoading}
          onReserveClick={(book) => setSelectedBookForReserve(book)}
        />
      ) : (
        <ReservationList
          reservations={reservations}
          isLoading={isLoading}
          onCancelReservation={handleCancelReservation}
          isCancellingId={isCancellingId}
        />
      )}

      {/* Reserve Modal */}
      {selectedBookForReserve && (
        <ReserveModal
          book={selectedBookForReserve}
          onClose={() => setSelectedBookForReserve(null)}
          onConfirm={handleReserveBook}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Add Book Modal */}
      {isAddBookOpen && (
        <AddBookModal
          onClose={() => setIsAddBookOpen(false)}
          onConfirm={handleAddBook}
          isSubmitting={isSubmitting}
        />
      )}
    </div>
  );
}
