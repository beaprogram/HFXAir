import {
  Shop,
  Item,
  Booking,
  SelectedVariant,
  ApiShop,
  ApiItem,
  ShopsApiResponse,
  ShopItemsApiResponse,
  AvailabilityStatus,
} from '../types/shops';
import { mockShops, mockItems } from '../data/mockShopsData';
import { generatePickupCode, calculateExpiryTime, getBookingStatus } from '../utils/shopHelpers';

const USE_MOCK_DATA = true;
const API_BASE_URL = 'http://172.171.1.217';

const ENDPOINTS = {
  SHOPS: `${API_BASE_URL}/shops`,
  SHOP_BY_ID: (id: string) => `${API_BASE_URL}/shops/${id}`,
  SHOP_HOURS: (id: string) => `${API_BASE_URL}/shops/${id}/hours`,
  SHOP_CATEGORIES: `${API_BASE_URL}/shops/categories`,
  SHOP_ITEMS: (shopId: string) => `${API_BASE_URL}/shops/${shopId}/items`,
  SHOP_CATALOG: (shopId: string) => `${API_BASE_URL}/shops/${shopId}/catalog`,
  ITEM_BY_ID: (id: string) => `${API_BASE_URL}/items/${id}`,
  SHOP_ITEM_CATEGORIES: (shopId: string) => `${API_BASE_URL}/shops/${shopId}/categories`,
  BOOKINGS: `${API_BASE_URL}/bookings`,
  CANCEL_BOOKING: (id: string) => `${API_BASE_URL}/bookings/${id}/cancel`,
};

const transformShop = (apiShop: ApiShop): Shop => ({
  id: String(apiShop.id),
  name: apiShop.name,
  category: apiShop.category,
  description: apiShop.description,
  location: apiShop.location,
  terminal: apiShop.terminal,
  gate: apiShop.gate,
  todayHours: {
    openTime: apiShop.today_hours.open_time,
    closeTime: apiShop.today_hours.close_time,
    isOpen: apiShop.today_hours.is_open,
    status: apiShop.today_hours.status,
    nextChange: apiShop.today_hours.next_change,
  },
  exceptionHours: (apiShop.exception_hours || []).map(eh => ({
    date: eh.date,
    description: eh.description,
    openTime: eh.open_time,
    closeTime: eh.close_time,
    isClosed: eh.is_closed,
  })),
  weeklyHours: (apiShop.weekly_hours || []).map(wh => ({
    day: wh.day,
    openTime: wh.open_time,
    closeTime: wh.close_time,
    isClosed: wh.is_closed,
  })),
});

const transformAvailability = (availability: string): AvailabilityStatus => {
  switch (availability.toLowerCase()) {
    case 'in_stock':
      return 'In Stock';
    case 'low_stock':
      return 'Low Stock';
    case 'out_of_stock':
      return 'Out of Stock';
    default:
      return 'In Stock';
  }
};

const transformItem = (apiItem: ApiItem, shopId: string, category: string = 'General'): Item => ({
  id: String(apiItem.item_id),
  shopId: shopId,
  name: apiItem.name,
  description: apiItem.description,
  basePrice: apiItem.base_price,
  currency: 'CAD',
  category: category,
  availability: transformAvailability(apiItem.availability),
  variantTypes: apiItem.variant_types || [],
  variants: (apiItem.variants || []).map(v => ({
    variantType: v.variant_type,
    variantValue: v.variant_value,
    priceAdjustment: v.price_adjustment,
    finalPrice: v.final_price,
  })),
});

export interface ServiceResponse<T> {
  data: T | null;
  error: string | null;
  success: boolean;
}

let mockBookings: Booking[] = [];

export const ShopService = {
  async getAllShops(params?: {
    category?: string;
    openNow?: boolean;
    sortBy?: string;
    terminal?: string;
    gate?: string;
  }): Promise<ServiceResponse<Shop[]>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(300);
      let result = [...mockShops];
      if (params?.category && params.category !== 'All') {
        result = result.filter(shop => shop.category === params.category);
      }
      return { data: result, error: null, success: true };
    }

    try {
      const queryParams = new URLSearchParams();
      if (params?.category && params.category !== 'All') {
        queryParams.append('category', params.category);
      }
      if (params?.openNow) queryParams.append('is_open', 'true');
      if (params?.sortBy) queryParams.append('sort_by', params.sortBy);
      if (params?.terminal) queryParams.append('terminal', params.terminal);
      if (params?.gate) queryParams.append('gate', params.gate);

      const url = queryParams.toString()
        ? `${ENDPOINTS.SHOPS}?${queryParams.toString()}`
        : ENDPOINTS.SHOPS;

      return { data: [], error: null, success: true };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },

  async getShopById(shopId: string): Promise<ServiceResponse<Shop>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(200);
      const shop = mockShops.find(s => s.id === shopId);
      if (!shop) {
        return { data: null, error: 'Shop not found', success: false };
      }
      return { data: shop, error: null, success: true };
    }

    try {
      return { data: null, error: 'Not implemented', success: false };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },

  async getShopCategories(): Promise<ServiceResponse<string[]>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(100);
      const categories = [...new Set(mockShops.map(s => s.category))];
      return { data: ['All', ...categories], error: null, success: true };
    }

    try {
      return { data: ['All'], error: null, success: true };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },
};

export const ItemService = {
  async getItemsByShop(
    shopId: string,
    params?: {
      category?: string;
      search?: string;
      minPrice?: number;
      maxPrice?: number;
      availability?: string;
      sortBy?: string;
    }
  ): Promise<ServiceResponse<Item[]>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(300);
      let result = mockItems.filter(item => item.shopId === shopId);

      if (params?.category && params.category !== 'All') {
        result = result.filter(item => item.category === params.category);
      }
      if (params?.search) {
        const query = params.search.toLowerCase();
        result = result.filter(
          item =>
            item.name.toLowerCase().includes(query) ||
            item.description.toLowerCase().includes(query)
        );
      }
      if (params?.minPrice !== undefined) {
        result = result.filter(item => item.basePrice >= params.minPrice!);
      }
      if (params?.maxPrice !== undefined) {
        result = result.filter(item => item.basePrice <= params.maxPrice!);
      }

      return { data: result, error: null, success: true };
    }

    try {
      const queryParams = new URLSearchParams();
      if (params?.category && params.category !== 'All') {
        queryParams.append('category', params.category);
      }
      if (params?.search) queryParams.append('search', params.search);
      if (params?.minPrice !== undefined) {
        queryParams.append('min_price', params.minPrice.toString());
      }
      if (params?.maxPrice !== undefined) {
        queryParams.append('max_price', params.maxPrice.toString());
      }
      if (params?.availability) queryParams.append('availability', params.availability);
      if (params?.sortBy) queryParams.append('sort_by', params.sortBy);

      const url = queryParams.toString()
        ? `${ENDPOINTS.SHOP_ITEMS(shopId)}?${queryParams.toString()}`
        : ENDPOINTS.SHOP_ITEMS(shopId);

      return { data: [], error: null, success: true };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },

  async getItemById(itemId: string, shopId?: string): Promise<ServiceResponse<Item>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(200);
      const item = mockItems.find(i => i.id === itemId);
      if (!item) {
        return { data: null, error: 'Item not found', success: false };
      }
      return { data: item, error: null, success: true };
    }

    try {
      return { data: null, error: 'Not implemented', success: false };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },

  async getItemCategories(shopId: string): Promise<ServiceResponse<string[]>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(100);
      const shopItems = mockItems.filter(item => item.shopId === shopId);
      const categories = [...new Set(shopItems.map(item => item.category))];
      return { data: ['All', ...categories], error: null, success: true };
    }

    try {
      return { data: ['All'], error: null, success: true };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },
};

export interface CreateBookingParams {
  itemId: string;
  shopId: string;
  quantity: number;
  selectedVariants?: SelectedVariant[];
}

export const BookingService = {
  async getAllBookings(): Promise<ServiceResponse<Booking[]>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(300);
      const updatedBookings = mockBookings.map(booking => ({
        ...booking,
        status: getBookingStatus(booking),
      }));
      return { data: updatedBookings, error: null, success: true };
    }

    try {
      return { data: [], error: null, success: true };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },

  async createBooking(params: CreateBookingParams): Promise<ServiceResponse<Booking>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(500);

      const shop = mockShops.find(s => s.id === params.shopId);
      const item = mockItems.find(i => i.id === params.itemId);

      if (!shop || !item) {
        return { data: null, error: 'Shop or item not found', success: false };
      }

      const existingBooking = mockBookings.find(
        b =>
          b.itemId === params.itemId &&
          (getBookingStatus(b) === 'Active' || getBookingStatus(b) === 'Expiring Soon')
      );

      if (existingBooking) {
        return {
          data: null,
          error: 'You already have an active reservation for this item',
          success: false,
        };
      }

      if (params.quantity > 3) {
        return { data: null, error: 'Maximum 3 items per reservation', success: false };
      }

      let totalPrice = item.basePrice * params.quantity;
      if (params.selectedVariants) {
        params.selectedVariants.forEach(variant => {
          totalPrice += variant.priceAdjustment * params.quantity;
        });
      }

      const newBooking: Booking = {
        id: `booking-${Date.now()}`,
        itemId: params.itemId,
        shopId: params.shopId,
        item: item,
        shop: shop,
        quantity: params.quantity,
        selectedVariants: params.selectedVariants,
        totalPrice,
        status: 'Active',
        createdAt: new Date(),
        expiresAt: calculateExpiryTime(),
        pickupCode: generatePickupCode(),
      };

      mockBookings.push(newBooking);

      return { data: newBooking, error: null, success: true };
    }

    try {
      return { data: null, error: 'Not implemented', success: false };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },

  async cancelBooking(bookingId: string): Promise<ServiceResponse<Booking>> {
    if (USE_MOCK_DATA) {
      await simulateDelay(300);

      const bookingIndex = mockBookings.findIndex(b => b.id === bookingId);

      if (bookingIndex === -1) {
        return { data: null, error: 'Reservation not found', success: false };
      }

      const booking = mockBookings[bookingIndex];
      const currentStatus = getBookingStatus(booking);

      if (currentStatus !== 'Active' && currentStatus !== 'Expiring Soon') {
        return { data: null, error: 'Only active reservations can be cancelled', success: false };
      }

      const updatedBooking: Booking = {
        ...booking,
        status: 'Cancelled',
        cancelledAt: new Date(),
      };

      mockBookings[bookingIndex] = updatedBooking;

      return { data: updatedBooking, error: null, success: true };
    }

    try {
      return { data: null, error: 'Not implemented', success: false };
    } catch (error: any) {
      return {
        data: null,
        error: error.response?.data?.message || error.message,
        success: false,
      };
    }
  },

  async getActiveCount(): Promise<ServiceResponse<number>> {
    if (USE_MOCK_DATA) {
      const count = mockBookings.filter(b => {
        const status = getBookingStatus(b);
        return status === 'Active' || status === 'Expiring Soon';
      }).length;
      return { data: count, error: null, success: true };
    }

    return { data: 0, error: null, success: true };
  },
};

const simulateDelay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));