import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, TextInput } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';

interface FilterOption {
  id: string;
  label: string;
}

interface FilterBarProps {
  filters: FilterOption[];
  selectedFilter: string;
  onFilterChange: (filterId: string) => void;
  showOpenNowToggle?: boolean;
  openNowActive?: boolean;
  onOpenNowToggle?: () => void;
  showSearch?: boolean;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
}

export default function FilterBar({
  filters,
  selectedFilter,
  onFilterChange,
  showOpenNowToggle = false,
  openNowActive = false,
  onOpenNowToggle,
  showSearch = false,
  searchValue = '',
  onSearchChange,
  searchPlaceholder = 'Search...',
}: FilterBarProps) {
  return (
    <View style={styles.container}>
      {showSearch && (
        <View style={styles.searchContainer}>
          <FontAwesome name="search" size={16} color="#666" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder={searchPlaceholder}
            placeholderTextColor="#999"
            value={searchValue}
            onChangeText={onSearchChange}
          />
          {searchValue.length > 0 && (
            <TouchableOpacity onPress={() => onSearchChange?.('')}>
              <FontAwesome name="times-circle" size={16} color="#999" />
            </TouchableOpacity>
          )}
        </View>
      )}

      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterScroll}>
        {showOpenNowToggle && (
          <TouchableOpacity
            style={[styles.filterButton, openNowActive && styles.filterButtonActive]}
            onPress={onOpenNowToggle}
          >
            <FontAwesome name="clock-o" size={12} color={openNowActive ? '#FFD100' : '#666'} style={styles.filterIcon} />
            <Text style={[styles.filterText, openNowActive && styles.filterTextActive]}>Open Now</Text>
          </TouchableOpacity>
        )}

        {filters.map(filter => (
          <TouchableOpacity
            key={filter.id}
            style={[styles.filterButton, selectedFilter === filter.id && styles.filterButtonActive]}
            onPress={() => onFilterChange(filter.id)}
          >
            <Text style={[styles.filterText, selectedFilter === filter.id && styles.filterTextActive]}>
              {filter.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  searchContainer: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f5f5f5', marginHorizontal: 16, marginTop: 12, marginBottom: 8, paddingHorizontal: 12, borderRadius: 10, height: 40 },
  searchIcon: { marginRight: 8 },
  searchInput: { flex: 1, fontSize: 14, color: '#333', height: 40 },
  filterScroll: { paddingHorizontal: 16, paddingVertical: 12, gap: 8 },
  filterButton: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, backgroundColor: '#f5f5f5', marginRight: 8 },
  filterButtonActive: { backgroundColor: '#0C2340' },
  filterIcon: { marginRight: 6 },
  filterText: { fontSize: 13, color: '#666', fontWeight: '600' },
  filterTextActive: { color: '#FFD100' },
});