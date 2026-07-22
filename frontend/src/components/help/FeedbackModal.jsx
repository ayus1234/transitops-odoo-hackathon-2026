import React, { useState } from 'react';
import Modal from '../ui/Modal';
import { helpApi } from '../../services/helpApi';
import { useToast } from '../../contexts/ToastContext';

const FeedbackModal = ({ isOpen, onClose, defaultPage = "" }) => {
  const { showToast } = useToast();
  const [rating, setRating] = useState(5);
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      const res = await helpApi.submitFeedback({
        rating,
        title: title || undefined,
        message: message || undefined,
        page: defaultPage || window.location.pathname
      });
      
      if (res.data?.success) {
        showToast('Thank you for your feedback!', 'success');
        onClose();
        // Reset form
        setRating(5);
        setTitle('');
        setMessage('');
      }
    } catch (error) {
      console.error("Failed to submit feedback", error);
      showToast('Failed to submit feedback. Please try again.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Submit Feedback" maxWidth="min-w-[320px] sm:min-w-[400px] max-w-md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-on-surface mb-2">
            How would you rate your experience? *
          </label>
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                className={`p-2 rounded-full transition-colors ${
                  star <= rating 
                    ? 'text-amber-500 hover:bg-amber-500/10' 
                    : 'text-on-surface-variant hover:bg-surface-container-high'
                }`}
              >
                <span className={`material-symbols-outlined text-3xl ${star <= rating ? 'fill-current font-variation-fill' : ''}`}>
                  star
                </span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="title" className="block text-sm font-medium text-on-surface mb-1">
            Summary (Optional)
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="Brief summary of your feedback"
            disabled={isSubmitting}
          />
        </div>

        <div>
          <label htmlFor="message" className="block text-sm font-medium text-on-surface mb-1">
            Details (Optional)
          </label>
          <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="Tell us more about your experience..."
            disabled={isSubmitting}
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-surface-container-high text-on-surface-variant font-bold rounded hover:bg-surface-variant transition-colors disabled:opacity-50"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-primary text-on-primary font-bold rounded hover:opacity-90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <span className="material-symbols-outlined animate-spin text-sm">refresh</span>
                Submitting...
              </span>
            ) : (
              'Submit Feedback'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default FeedbackModal;
