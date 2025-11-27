import React, { useState, useCallback } from 'react';
import { View, StyleSheet, ActivityIndicator, Text } from 'react-native';
import { ShopViewType } from '../../types/shops';
import { useShops, useShop, useItems, useBookings } from '../../hooks/useShops';
import ShopListView from '../shops/ShopListView';
import ShopDetailView from '../shops/ShopDetailView';
import CatalogView from '../shops/CatalogView';
import ItemDetailView from '../shops/ItemDetailView';
import MyReservationsView from '../shops/MyReservationsView';

interface ShopsScreenProps {
  showHeader?: boolean;
}

export default function ShopsScreen({ showHeader = true }: ShopsScreenProps) {
  const [currentView, setCurrentView] = useState<ShopViewType>('list');
  const [selectedShopId, setSelectedShopId] = useState<string | null>(null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);

  const { shops, loading: shopsLoading, error: shopsError } = useShops();
  const { shop: selectedShop } = useShop(selectedShopId);
  const { items: shopItems, updateItemAvailability } = useItems(selectedShopId);
  const { bookings, activeCount: activeBookingsCount, createBooking, cancelBooking } = useBookings();

  const selectedItem = selectedItemId ? shopItems.find(i => i.id === selectedItemId) || null : null;

  const navigateToShopDetail = useCallback((shopId: string) => {
    setSelectedShopId(shopId);
    setCurrentView('detail');
  }, []);

  const navigateToCatalog = useCallback(() => {
    setCurrentView('catalog');
  }, []);

  const navigateToItem = useCallback((itemId: string) => {
    setSelectedItemId(itemId);
    setCurrentView('item');
  }, []);

  const navigateToBookings = useCallback(() => {
    setCurrentView('bookings');
  }, []);

  const navigateBack = useCallback(() => {
    switch (currentView) {
      case 'detail':
        setCurrentView('list');
        setSelectedShopId(null);
        break;
      case 'catalog':
        setCurrentView('detail');
        break;
      case 'item':
        setCurrentView('catalog');
        setSelectedItemId(null);
        break;
      case 'bookings':
        setCurrentView('list');
        break;
      default:
        setCurrentView('list');
    }
  }, [currentView]);

  const handleBook = useCallback(async (bookingData: Parameters<typeof createBooking>[0]) => {
    const result = await createBooking(bookingData);
    if (result.success && result.booking) {
      return result.booking;
    }
    throw new Error(result.error || 'Failed to create reservation');
  }, [createBooking]);

  const handleCancelBooking = useCallback(async (bookingId: string) => {
    await cancelBooking(bookingId);
  }, [cancelBooking]);

  const handleRebookItem = useCallback((shopId: string, itemId: string) => {
    setSelectedShopId(shopId);
    setSelectedItemId(itemId);
    setCurrentView('item');
  }, []);

  const handleViewBookingDetail = useCallback((bookingId: string) => {
    const booking = bookings.find(b => b.id === bookingId);
    if (booking) {
      setSelectedShopId(booking.shopId);
      setSelectedItemId(booking.itemId);
      setCurrentView('item');
    }
  }, [bookings]);

  if (shopsLoading && currentView === 'list') {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0C2340" />
        <Text style={styles.loadingText}>Loading shops...</Text>
      </View>
    );
  }

  if (shopsError && currentView === 'list') {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Error: {shopsError}</Text>
      </View>
    );
  }

  const renderView = () => {
    switch (currentView) {
      case 'list':
        return (
          <ShopListView
            shops={shops}
            onShopPress={navigateToShopDetail}
            onMyBookingsPress={navigateToBookings}
            bookingsCount={activeBookingsCount}
          />
        );
      case 'detail':
        if (!selectedShop) return null;
        return (
          <ShopDetailView
            shop={selectedShop}
            onBack={navigateBack}
            onViewCatalog={navigateToCatalog}
          />
        );
      case 'catalog':
        if (!selectedShop) return null;
        return (
          <CatalogView
            shop={selectedShop}
            items={shopItems}
            onBack={navigateBack}
            onItemPress={navigateToItem}
          />
        );
      case 'item':
        if (!selectedShop || !selectedItem) return null;
        return (
          <ItemDetailView
            shop={selectedShop}
            item={selectedItem}
            existingBookings={bookings}
            onBack={navigateBack}
            onBook={handleBook}
          />
        );
      case 'bookings':
        return (
          <MyReservationsView
            bookings={bookings}
            onBack={navigateBack}
            onCancelBooking={handleCancelBooking}
            onRebookItem={handleRebookItem}
            onViewBookingDetail={handleViewBookingDetail}
          />
        );
      default:
        return null;
    }
  };

  return <View style={styles.container}>{renderView()}</View>;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f5f5f5' },
  loadingText: { marginTop: 12, fontSize: 14, color: '#666' },
  errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f5f5f5', padding: 20 },
  errorText: { fontSize: 14, color: '#C62828', textAlign: 'center' },
});