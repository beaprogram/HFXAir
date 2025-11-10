import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, StatusBar } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';

import ArrivalsScreen from './tabs/ArrivalsScreen';
import DeparturesScreen from './tabs/DeparturesScreen';
import ShopsScreen from './tabs/ShopsScreen';

interface HomeScreenProps {
  userData?: {ticketNumber: string, flightNumber: string} | null;
  onLogout?: () => void;
}

interface TileData {
  id: string;
  label: string;
  icon: string;
  accessibilityLabel: string;
}

const tiles: TileData[] = [
  { id: 'arrivals', label: 'Arrivals', icon: 'plane', accessibilityLabel: 'View flight arrivals' },
  { id: 'departures', label: 'Departures', icon: 'plane', accessibilityLabel: 'View flight departures' },
  { id: 'map', label: 'HFX Airport Map', icon: 'map', accessibilityLabel: 'View Halifax airport map' },
  { id: 'shops', label: 'Shops', icon: 'shopping-cart', accessibilityLabel: 'Browse airport shops' },
  { id: 'parking', label: 'Parking', icon: 'car', accessibilityLabel: 'View parking information' },
  { id: 'about', label: 'About', icon: 'info-circle', accessibilityLabel: 'About Halifax Stanfield Airport' },
];

export default function HomeScreen({ userData, onLogout }: HomeScreenProps) {
  const [selectedTab, setSelectedTab] = useState('arrivals');

  const renderContent = () => {
    switch (selectedTab) {
      case 'arrivals':
        return <ArrivalsScreen showHeader={false} />;
      
      case 'departures':
        return <DeparturesScreen showHeader={false} />;
      
      case 'shops':
        return <ShopsScreen showHeader={false} />;
      
      case 'map':
        return (
          <View style={styles.emptyContent}>
            <FontAwesome name="map" size={48} color="#ccc" />
            <Text style={styles.emptyText}>Airport Map - Coming Soon</Text>
          </View>
        );
      
      case 'parking':
        return (
          <View style={styles.emptyContent}>
            <FontAwesome name="car" size={48} color="#ccc" />
            <Text style={styles.emptyText}>Parking - Coming Soon</Text>
          </View>
        );
      
      case 'about':
        return (
          <View style={styles.emptyContent}>
            <FontAwesome name="info-circle" size={48} color="#ccc" />
            <Text style={styles.emptyText}>About - Coming Soon</Text>
          </View>
        );
      
      default:
        return (
          <View style={styles.emptyContent}>
            <FontAwesome name="hand-pointer-o" size={48} color="#ccc" />
            <Text style={styles.emptyText}>Select a section below</Text>
          </View>
        );
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0C2340" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Halifax Stanfield</Text>
        <Text style={styles.headerSubtitle}>International Airport</Text>
      </View>
      
      <View style={styles.mainContent}>
        {renderContent()}
      </View>

      <View style={styles.bottomNav}>
        <View style={styles.tilesRow}>
          {tiles.map((tile) => (
            <TouchableOpacity 
              key={tile.id} 
              style={[styles.navTile, selectedTab === tile.id && styles.selectedTile]} 
              onPress={() => setSelectedTab(tile.id)} 
              accessible={true} 
              accessibilityLabel={tile.accessibilityLabel} 
              accessibilityRole="button" 
              activeOpacity={0.7}
            >
              <FontAwesome 
                name={tile.icon} 
                size={20} 
                color={selectedTab === tile.id ? '#FFD100' : '#0C2340'} 
                style={tile.label === 'Arrivals' ? { transform: [{ rotate: '180deg' }] } : undefined} 
              />
              <Text style={[styles.navLabel, selectedTab === tile.id && styles.selectedLabel]}>
                {tile.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: '#f5f5f5' 
  },
  header: { 
    backgroundColor: '#0C2340', 
    paddingTop: 50, 
    paddingBottom: 20, 
    paddingHorizontal: 20, 
    alignItems: 'center' 
  },
  headerTitle: { 
    fontSize: 24, 
    fontWeight: 'bold', 
    color: '#fff' 
  },
  headerSubtitle: { 
    fontSize: 14, 
    color: '#FFD100', 
    marginTop: 4 
  },
  mainContent: { 
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  emptyContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    fontWeight: '500',
  },
  bottomNav: { 
    backgroundColor: '#fff', 
    borderTopWidth: 1, 
    borderTopColor: '#e0e0e0', 
    paddingVertical: 8, 
    paddingHorizontal: 8, 
    shadowColor: '#000', 
    shadowOffset: { width: 0, height: -2 }, 
    shadowOpacity: 0.1, 
    shadowRadius: 4, 
    elevation: 10 
  },
  tilesRow: { 
    flexDirection: 'row', 
    justifyContent: 'space-around' 
  },
  navTile: { 
    alignItems: 'center', 
    justifyContent: 'center', 
    paddingVertical: 8, 
    paddingHorizontal: 8, 
    minWidth: 60, 
    minHeight: 44, 
    borderRadius: 8,
  },
  selectedTile: { 
    backgroundColor: '#0C2340' 
  },
  navLabel: { 
    fontSize: 10, 
    color: '#0C2340', 
    marginTop: 4, 
    fontWeight: '600', 
    textAlign: 'center' 
  },
  selectedLabel: { 
    color: '#FFD100' 
  },
});