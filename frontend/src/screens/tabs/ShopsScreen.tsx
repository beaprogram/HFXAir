import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, StatusBar } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';

interface ShopsScreenProps {
  showHeader?: boolean;
}

const shops = [
  {
    id: '1',
    name: 'Duty Free Atlantic',
    category: 'Duty Free',
    location: 'International Departures',
    hours: '5:00 AM - 11:00 PM',
    description: 'Perfumes, liquor, tobacco, and gifts',
  },
  {
    id: '2',
    name: 'Tim Hortons',
    category: 'Food & Beverage',
    location: 'Domestic Terminal',
    hours: '4:30 AM - 10:00 PM',
    description: 'Coffee, donuts, and sandwiches',
  },
  {
    id: '3',
    name: 'Hudson News',
    category: 'Retail',
    location: 'Main Concourse',
    hours: '5:00 AM - 9:00 PM',
    description: 'Books, magazines, snacks, and travel essentials',
  },
  {
    id: '4',
    name: 'Starbucks',
    category: 'Food & Beverage',
    location: 'Pre-Security Area',
    hours: '4:00 AM - 11:00 PM',
    description: 'Premium coffee and light meals',
  },
  {
    id: '5',
    name: 'Atlantic News',
    category: 'Retail',
    location: 'Gate Area B',
    hours: '5:00 AM - 10:00 PM',
    description: 'Newspapers, snacks, and souvenirs',
  },
  {
    id: '6',
    name: 'Relay',
    category: 'Retail',
    location: 'Gate Area C',
    hours: '5:30 AM - 9:00 PM',
    description: 'Travel convenience store',
  },
  {
    id: '7',
    name: "McDonald's",
    category: 'Food & Beverage',
    location: 'Food Court',
    hours: '5:00 AM - 10:00 PM',
    description: 'Fast food and breakfast',
  },
  {
    id: '8',
    name: 'Maritime Souvenirs',
    category: 'Retail',
    location: 'Main Terminal',
    hours: '6:00 AM - 9:00 PM',
    description: 'Local crafts and Nova Scotia gifts',
  },
];

export default function ShopsScreen({ showHeader = true }: ShopsScreenProps) {
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', 'Food & Beverage', 'Retail', 'Duty Free'];

  const filteredShops = selectedCategory === 'All' 
    ? shops 
    : shops.filter(shop => shop.category === selectedCategory);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Food & Beverage':
        return 'cutlery';
      case 'Retail':
        return 'shopping-bag';
      case 'Duty Free':
        return 'gift';
      default:
        return 'shopping-cart';
    }
  };

  return (
    <View style={showHeader ? styles.container : styles.containerNoHeader}>
      {showHeader && <StatusBar barStyle="light-content" backgroundColor="#0C2340" />}
      
      {/* Header - only show if showHeader is true */}
      {showHeader && (
        <View style={styles.header}>
          <View style={styles.headerTitleContainer}>
            <FontAwesome name="shopping-cart" size={20} color="#FFD100" />
            <Text style={styles.headerTitle}>Shops & Dining</Text>
          </View>
        </View>
      )}

      {/* Embedded Header - only show when embedded in home */}
      {!showHeader && (
        <View style={styles.embeddedHeader}>
          <Text style={styles.subtitle}>Shops & Dining</Text>
        </View>
      )}

      {/* Category Filter */}
      <View style={styles.filterContainer}>
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterScroll}
        >
          {categories.map((category) => (
            <TouchableOpacity
              key={category}
              style={[
                styles.filterButton,
                selectedCategory === category && styles.filterButtonActive
              ]}
              onPress={() => setSelectedCategory(category)}
            >
              <Text style={[
                styles.filterText,
                selectedCategory === category && styles.filterTextActive
              ]}>
                {category}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Content */}
      <ScrollView 
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.content}>
          {filteredShops.map((shop) => (
            <View key={shop.id} style={styles.shopCard}>
              <View style={styles.cardHeader}>
                <View style={styles.iconContainer}>
                  <FontAwesome 
                    name={getCategoryIcon(shop.category)} 
                    size={24} 
                    color="#0C2340" 
                  />
                </View>
                <View style={styles.shopInfo}>
                  <Text style={styles.shopName}>{shop.name}</Text>
                  <View style={styles.categoryBadge}>
                    <Text style={styles.categoryText}>{shop.category}</Text>
                  </View>
                </View>
              </View>

              <Text style={styles.description}>{shop.description}</Text>

              <View style={styles.detailsRow}>
                <View style={styles.detailItem}>
                  <FontAwesome name="map-marker" size={14} color="#666" />
                  <Text style={styles.detailText}>{shop.location}</Text>
                </View>
              </View>

              <View style={styles.detailsRow}>
                <View style={styles.detailItem}>
                  <FontAwesome name="clock-o" size={14} color="#666" />
                  <Text style={styles.detailText}>{shop.hours}</Text>
                </View>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  containerNoHeader: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  header: {
    backgroundColor: '#0C2340',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  embeddedHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  subtitle: { 
    fontSize: 18, 
    fontWeight: '600', 
    color: '#0C2340' 
  },
  filterContainer: {
    backgroundColor: '#fff',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  filterScroll: {
    paddingHorizontal: 16,
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
    marginRight: 8,
  },
  filterButtonActive: {
    backgroundColor: '#0C2340',
  },
  filterText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  filterTextActive: {
    color: '#FFD100',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  shopCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#FFD100',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  shopInfo: {
    flex: 1,
  },
  shopName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0C2340',
    marginBottom: 6,
  },
  categoryBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryText: {
    fontSize: 11,
    color: '#1976D2',
    fontWeight: '600',
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  detailsRow: {
    marginBottom: 8,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  detailText: {
    fontSize: 13,
    color: '#666',
  },
});