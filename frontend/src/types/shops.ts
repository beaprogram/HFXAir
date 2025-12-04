export interface ShopsApiResponse {
  filters_applied: Record<string, any>;
  shops: ApiShop[];
}

export interface ShopItemsApiResponse {
  items: ApiItem[];
}

export interface ShopCatalogApiResponse {
  categories: ApiCatalogCategory[];
}

export interface ShopCategoriesApiResponse {
  categories: ApiShopCategory[];
}

export interface ShopItemCategoriesApiResponse {
  categories: ApiItemCategory[];
  shop_id: number;
  shop_name: string;
}

export interface ApiShop {
  id: number;
  name: string;
  category: string;
  description: string;
  location: string;
  terminal: string;
  gate: string | null;
  today_hours: ApiTodayHours;
  exception_hours?: ApiExceptionHours[];
  weekly_hours?: ApiWeeklyHours[];
}

export interface ApiTodayHours {
  open_time: string;
  close_time: string;
  is_open: boolean;
  status: string;
  next_change: string | null;
}

export interface ApiWeeklyHours {
  day: string;
  open_time: string | null;
  close_time: string | null;
  is_closed: boolean;
}

export interface ApiExceptionHours {
  date: string;
  description: string;
  open_time: string | null;
  close_time: string | null;
  is_closed: boolean;
}

export interface ApiShopCategory {
  name: string;
  count: number;
}

export interface ApiItem {
  item_id: number;
  name: string;
  description: string;
  base_price: number;
  availability: string;
  variant_types?: string[];
  variants?: ApiVariant[];
}

export interface ApiVariant {
  variant_type: string;
  variant_value: string;
  price_adjustment: number;
  final_price: number;
}

export interface ApiCatalogCategory {
  category_id: number;
  category_name: string;
  items: ApiCatalogItem[];
}

export interface ApiCatalogItem {
  item_id: number;
  name: string;
  description: string;
  base_price: number;
}

export interface ApiItemCategory {
  category_id: number;
  category_name: string;
  item_count: number;
}

export interface Shop {
  id: string;
  name: string;
  category: string;
  description: string;
  location: string;
  terminal: string;
  gate: string | null;
  todayHours: TodayHours;
  exceptionHours: ExceptionHours[];
  weeklyHours: WeeklyHours[];
}

export interface TodayHours {
  openTime: string;
  closeTime: string;
  isOpen: boolean;
  status: string;
  nextChange: string | null;
}

export interface WeeklyHours {
  day: string;
  openTime: string | null;
  closeTime: string | null;
  isClosed: boolean;
}

export interface ExceptionHours {
  date: string;
  description: string;
  openTime: string | null;
  closeTime: string | null;
  isClosed: boolean;
}

export interface Item {
  id: string;
  shopId: string;
  name: string;
  description: string;
  basePrice: number;
  currency: string;
  category: string;
  availability: AvailabilityStatus;
  variantTypes: string[];
  variants: Variant[];
}

export interface Variant {
  variantType: string;
  variantValue: string;
  priceAdjustment: number;
  finalPrice: number;
}

export interface ItemCategory {
  id: string;
  name: string;
  itemCount: number;
}

export type AvailabilityStatus = 'In Stock' | 'Low Stock' | 'Out of Stock';

export interface Booking {
  id: string;
  itemId: string;
  shopId: string;
  item: Item;
  shop: Shop;
  quantity: number;
  selectedVariants?: SelectedVariant[];
  totalPrice: number;
  status: BookingStatus;
  createdAt: Date;
  expiresAt: Date;
  pickupCode: string;
  pickedUpAt?: Date;
  cancelledAt?: Date;
}

export interface SelectedVariant {
  variantType: string;
  variantValue: string;
  priceAdjustment: number;
}

export type BookingStatus = 'Active' | 'Expiring Soon' | 'Expired' | 'Picked Up' | 'Cancelled';

export type ShopSortOption = 'name' | 'gate' | 'status';
export type CatalogSortOption = 'name' | 'price-asc' | 'price-desc';

export type ShopViewType = 'list' | 'detail' | 'catalog' | 'item' | 'bookings';