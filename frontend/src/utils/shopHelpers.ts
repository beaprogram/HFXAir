import { Shop, Booking, BookingStatus, AvailabilityStatus } from '../types/shops';

export const formatTime = (time: string | null): string => {
  if (!time) return 'N/A';
  const cleanTime = time.replace(/:$/, '');
  const [hours, minutes] = cleanTime.split(':').map(Number);
  if (isNaN(hours)) return time;
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  const displayMinutes = minutes || 0;
  return `${displayHours}:${displayMinutes.toString().padStart(2, '0')} ${period}`;
};

export const getCurrentDay = (): string => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  return days[new Date().getDay()];
};

export const getShopStatusText = (shop: Shop): { text: string; isOpen: boolean } => {
  const { todayHours } = shop;
  if (todayHours.isOpen) {
    return {
      text: `Closes ${formatTime(todayHours.closeTime)}`,
      isOpen: true,
    };
  }
  if (todayHours.nextChange) {
    return {
      text: `Opens ${formatTime(todayHours.nextChange)}`,
      isOpen: false,
    };
  }
  return {
    text: `Opens ${formatTime(todayHours.openTime)}`,
    isOpen: false,
  };
};

export const isShopOpen = (shop: Shop): boolean => {
  return shop.todayHours.isOpen;
};

export const getTodayHours = (shop: Shop) => {
  return {
    open: shop.todayHours.openTime,
    close: shop.todayHours.closeTime,
    isClosed: !shop.todayHours.isOpen,
  };
};

export const getTimeRemaining = (
  expiresAt: Date
): { hours: number; minutes: number; seconds: number; total: number } => {
  const now = new Date().getTime();
  const expiry = new Date(expiresAt).getTime();
  const total = Math.max(0, expiry - now);
  const hours = Math.floor(total / (1000 * 60 * 60));
  const minutes = Math.floor((total % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((total % (1000 * 60)) / 1000);
  return { hours, minutes, seconds, total };
};

export const formatCountdown = (expiresAt: Date): string => {
  const { hours, minutes, seconds } = getTimeRemaining(expiresAt);
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

export const getBookingStatus = (booking: Booking): BookingStatus => {
  if (booking.status === 'Picked Up' || booking.status === 'Cancelled') {
    return booking.status;
  }
  const { total } = getTimeRemaining(booking.expiresAt);
  if (total <= 0) return 'Expired';
  if (total <= 2 * 60 * 60 * 1000) return 'Expiring Soon';
  return 'Active';
};

export const generatePickupCode = (): string => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
};

export const calculateExpiryTime = (): Date => {
  const now = new Date();
  return new Date(now.getTime() + 24 * 60 * 60 * 1000);
};

export const formatPrice = (price: number, currency: string = 'CAD'): string => {
  return `$${price.toFixed(2)} ${currency}`;
};

export const getAvailabilityColor = (status: AvailabilityStatus): string => {
  switch (status) {
    case 'In Stock':
      return '#4CAF50';
    case 'Low Stock':
      return '#FF9800';
    case 'Out of Stock':
      return '#F44336';
    default:
      return '#666';
  }
};

export const formatDate = (date: Date): string => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};