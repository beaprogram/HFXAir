import { useState, useEffect, useCallback } from 'react';
import { Shop, Item, Booking } from '../types/shops';
import {
  ShopService,
  ItemService,
  BookingService,
  CreateBookingParams,
} from '../services/shopService';
import { getBookingStatus } from '../utils/shopHelpers';

export function useShops() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchShops = useCallback(async () => {
    setLoading(true);
    setError(null);
    const response = await ShopService.getAllShops();
    if (!response.success) {
      setError(response.error);
    } else {
      setShops(response.data || []);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchShops();
  }, [fetchShops]);

  return { shops, loading, error, refetch: fetchShops };
}

export function useShop(shopId: string | null) {
  const [shop, setShop] = useState<Shop | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!shopId) {
      setShop(null);
      return;
    }

    const fetchShop = async () => {
      setLoading(true);
      setError(null);
      const response = await ShopService.getShopById(shopId);
      if (!response.success) {
        setError(response.error);
      } else {
        setShop(response.data);
      }
      setLoading(false);
    };

    fetchShop();
  }, [shopId]);

  return { shop, loading, error };
}

export function useItems(shopId: string | null) {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchItems = useCallback(async () => {
    if (!shopId) {
      setItems([]);
      return;
    }

    setLoading(true);
    setError(null);
    const response = await ItemService.getItemsByShop(shopId);
    if (!response.success) {
      setError(response.error);
    } else {
      setItems(response.data || []);
    }
    setLoading(false);
  }, [shopId]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const updateItemAvailability = useCallback((itemId: string, availability: Item['availability']) => {
    setItems(prev =>
      prev.map(item => {
        if (item.id === itemId) {
          return { ...item, availability };
        }
        return item;
      })
    );
  }, []);

  return { items, loading, error, refetch: fetchItems, updateItemAvailability };
}

export function useItemCategories(shopId: string | null) {
  const [categories, setCategories] = useState<string[]>(['All']);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!shopId) {
      setCategories(['All']);
      return;
    }

    const fetchCategories = async () => {
      setLoading(true);
      const response = await ItemService.getItemCategories(shopId);
      if (response.success && response.data) {
        setCategories(response.data);
      }
      setLoading(false);
    };

    fetchCategories();
  }, [shopId]);

  return { categories, loading };
}

export function useBookings() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBookings = useCallback(async () => {
    setLoading(true);
    setError(null);
    const response = await BookingService.getAllBookings();
    if (!response.success) {
      setError(response.error);
    } else {
      setBookings(response.data || []);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchBookings();
  }, [fetchBookings]);

  const createBooking = useCallback(
    async (
      params: CreateBookingParams
    ): Promise<{ success: boolean; booking?: Booking; error?: string }> => {
      const response = await BookingService.createBooking(params);
      if (!response.success) {
        return { success: false, error: response.error || 'Failed to create reservation' };
      }
      if (response.data) {
        setBookings(prev => [...prev, response.data!]);
        return { success: true, booking: response.data };
      }
      return { success: false, error: 'Unknown error occurred' };
    },
    []
  );

  const cancelBooking = useCallback(
    async (bookingId: string): Promise<{ success: boolean; error?: string }> => {
      const response = await BookingService.cancelBooking(bookingId);
      if (!response.success) {
        return { success: false, error: response.error || 'Failed to cancel reservation' };
      }
      if (response.data) {
        setBookings(prev => prev.map(b => (b.id === bookingId ? response.data! : b)));
        return { success: true };
      }
      return { success: false, error: 'Unknown error occurred' };
    },
    []
  );

  const activeBookings = bookings.filter(b => {
    const status = getBookingStatus(b);
    return status === 'Active' || status === 'Expiring Soon';
  });

  const historyBookings = bookings.filter(b => {
    const status = getBookingStatus(b);
    return status === 'Expired' || status === 'Cancelled' || status === 'Picked Up';
  });

  return {
    bookings,
    activeBookings,
    historyBookings,
    activeCount: activeBookings.length,
    loading,
    error,
    refetch: fetchBookings,
    createBooking,
    cancelBooking,
  };
}