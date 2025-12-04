import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  FlatList,
  ScrollView,
} from 'react-native';
import MapView, { Marker, Polyline, PROVIDER_GOOGLE } from 'react-native-maps';
import { POIType, PointOfInterest } from '../../types/MapTypes';
import { airportPOIs } from '../../data/mapData';

const AIRPORT_CENTER = {
  latitude: 44.8808,
  longitude: -63.5085,
  latitudeDelta: 0.004,
  longitudeDelta: 0.004,
};

const MY_LOCATION = { 
  latitude: 44.8803, 
  longitude: -63.5082 
};

const TYPE_COLORS: Record<POIType, string> = {
  gate: '#3B82F6',
  restaurant: '#F97316',
  shop: '#FBBF24',
  charging: '#22C55E',
  restroom: '#A855F7',
  info: '#06B6D4',
  security: '#6B7280',
};

const TYPE_ICONS: Record<POIType, string> = {
  gate: '✈️',
  restaurant: '🍽️',
  shop: '🛍️',
  charging: '⚡',
  restroom: '🚻',
  info: 'ℹ️',
  security: '🛡️',
};

// Custom map style to hide roads/transit lines
const MAP_STYLE = [
  {
    featureType: 'transit',
    elementType: 'all',
    stylers: [{ visibility: 'off' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry.stroke',
    stylers: [{ visibility: 'off' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry.fill',
    stylers: [{ color: '#ffffff' }],
  },
  {
    featureType: 'road',
    elementType: 'labels',
    stylers: [{ visibility: 'off' }],
  },
  {
    featureType: 'poi',
    elementType: 'all',
    stylers: [{ visibility: 'off' }],
  },
  {
    featureType: 'landscape',
    elementType: 'geometry.fill',
    stylers: [{ color: '#f5f5f5' }],
  },
];

function calcDistance(poi: PointOfInterest): number {
  const R = 6371000;
  const dLat = (poi.latitude - MY_LOCATION.latitude) * Math.PI / 180;
  const dLon = (poi.longitude - MY_LOCATION.longitude) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(MY_LOCATION.latitude * Math.PI / 180) *
    Math.cos(poi.latitude * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function formatDistance(meters: number): string {
  return meters < 1000 ? `${Math.round(meters)}m` : `${(meters / 1000).toFixed(1)}km`;
}

function calcWalkTime(meters: number): number {
  return Math.max(1, Math.ceil(meters / 72));
}

export default function MapScreen() {
  const mapRef = useRef<MapView>(null);
  const [activeFilter, setActiveFilter] = useState<POIType | 'all'>('all');
  const [selectedPOI, setSelectedPOI] = useState<PointOfInterest | null>(null);
  const [showMap, setShowMap] = useState(false);
  const [navigating, setNavigating] = useState<PointOfInterest | null>(null);

  const filteredPOIs = activeFilter === 'all' 
    ? airportPOIs 
    : airportPOIs.filter(p => p.type === activeFilter);
  
  const sortedPOIs = [...filteredPOIs].sort((a, b) => calcDistance(a) - calcDistance(b));

  function startNav(poi: PointOfInterest) {
    setNavigating(poi);
    setSelectedPOI(null);
    setShowMap(true);
    setTimeout(() => {
      mapRef.current?.fitToCoordinates(
        [MY_LOCATION, { latitude: poi.latitude, longitude: poi.longitude }],
        { edgePadding: { top: 100, right: 60, bottom: 280, left: 60 }, animated: true }
      );
    }, 300);
  }

  function stopNav() {
    setNavigating(null);
    mapRef.current?.animateToRegion(AIRPORT_CENTER, 300);
  }

  function goToNearest(type: POIType) {
    const items = airportPOIs.filter(p => p.type === type);
    if (items.length === 0) return;
    
    let nearest = items[0];
    let minDist = calcDistance(items[0]);
    
    for (const item of items) {
      const dist = calcDistance(item);
      if (dist < minDist) {
        minDist = dist;
        nearest = item;
      }
    }
    startNav(nearest);
  }

  function renderListItem({ item }: { item: PointOfInterest }) {
    const dist = calcDistance(item);
    const walkTime = calcWalkTime(dist);
    const color = TYPE_COLORS[item.type];
    const icon = TYPE_ICONS[item.type];

    return (
      <TouchableOpacity style={styles.listCard} onPress={() => setSelectedPOI(item)}>
        <View style={[styles.listCardIcon, { backgroundColor: color + '20' }]}>
          <Text style={styles.listCardEmoji}>{icon}</Text>
        </View>
        <View style={styles.listCardContent}>
          <Text style={styles.listCardTitle}>{item.name}</Text>
          <Text style={styles.listCardSubtitle}>
            {formatDistance(dist)} • {walkTime} min walk
          </Text>
        </View>
        <TouchableOpacity 
          style={[styles.listCardButton, { backgroundColor: color }]}
          onPress={() => startNav(item)}
        >
          <Text style={styles.listCardButtonText}>Go</Text>
        </TouchableOpacity>
      </TouchableOpacity>
    );
  }

  return (
    <View style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerSub}>Halifax Stanfield</Text>
          <Text style={styles.headerTitle}>Explore Airport</Text>
        </View>
        <TouchableOpacity 
          style={styles.headerToggle}
          onPress={() => setShowMap(!showMap)}
        >
          <Text style={styles.headerToggleText}>{showMap ? '📋' : '🗺️'}</Text>
        </TouchableOpacity>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.quickBtn} onPress={() => goToNearest('gate')}>
          <View style={[styles.quickBtnIcon, { backgroundColor: '#DBEAFE' }]}>
            <Text style={styles.quickBtnEmoji}>✈️</Text>
          </View>
          <Text style={styles.quickBtnLabel}>Gates</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.quickBtn} onPress={() => goToNearest('restaurant')}>
          <View style={[styles.quickBtnIcon, { backgroundColor: '#FFEDD5' }]}>
            <Text style={styles.quickBtnEmoji}>🍽️</Text>
          </View>
          <Text style={styles.quickBtnLabel}>Food</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.quickBtn} onPress={() => goToNearest('restroom')}>
          <View style={[styles.quickBtnIcon, { backgroundColor: '#F3E8FF' }]}>
            <Text style={styles.quickBtnEmoji}>🚻</Text>
          </View>
          <Text style={styles.quickBtnLabel}>WC</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.quickBtn} onPress={() => goToNearest('charging')}>
          <View style={[styles.quickBtnIcon, { backgroundColor: '#DCFCE7' }]}>
            <Text style={styles.quickBtnEmoji}>⚡</Text>
          </View>
          <Text style={styles.quickBtnLabel}>Charge</Text>
        </TouchableOpacity>
      </View>

      {/* Filter Chips */}
      <View style={styles.filterWrapper}>
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterContainer}
        >
          <TouchableOpacity 
            style={[styles.filterChip, activeFilter === 'all' && styles.filterChipActive]}
            onPress={() => setActiveFilter('all')}
          >
            <Text style={[styles.filterChipText, activeFilter === 'all' && styles.filterChipTextActive]}>
              All
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilter === 'gate' && styles.filterChipActive]}
            onPress={() => setActiveFilter('gate')}
          >
            <Text style={[styles.filterChipText, activeFilter === 'gate' && styles.filterChipTextActive]}>
              Gates
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilter === 'restaurant' && styles.filterChipActive]}
            onPress={() => setActiveFilter('restaurant')}
          >
            <Text style={[styles.filterChipText, activeFilter === 'restaurant' && styles.filterChipTextActive]}>
              Food
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilter === 'shop' && styles.filterChipActive]}
            onPress={() => setActiveFilter('shop')}
          >
            <Text style={[styles.filterChipText, activeFilter === 'shop' && styles.filterChipTextActive]}>
              Shops
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilter === 'restroom' && styles.filterChipActive]}
            onPress={() => setActiveFilter('restroom')}
          >
            <Text style={[styles.filterChipText, activeFilter === 'restroom' && styles.filterChipTextActive]}>
              WC
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilter === 'charging' && styles.filterChipActive]}
            onPress={() => setActiveFilter('charging')}
          >
            <Text style={[styles.filterChipText, activeFilter === 'charging' && styles.filterChipTextActive]}>
              Charging
            </Text>
          </TouchableOpacity>
        </ScrollView>
      </View>

      {/* Main Content */}
      {showMap ? (
        <View style={styles.mapContainer}>
          <MapView
            ref={mapRef}
            provider={PROVIDER_GOOGLE}
            style={styles.map}
            initialRegion={AIRPORT_CENTER}
            minZoomLevel={16}
            maxZoomLevel={20}
            toolbarEnabled={false}
            customMapStyle={MAP_STYLE}
          >
            <Marker
              coordinate={MY_LOCATION}
              pinColor="#EF4444"
              title="You"
            />
            
            {(navigating ? [navigating] : filteredPOIs).map(poi => (
              <Marker
                key={poi.id}
                coordinate={{ latitude: poi.latitude, longitude: poi.longitude }}
                pinColor={TYPE_COLORS[poi.type]}
                title={poi.name}
                onPress={() => !navigating && setSelectedPOI(poi)}
              />
            ))}
            
            {navigating && (
              <Polyline
                key={`nav-${navigating.id}`}
                coordinates={[
                  MY_LOCATION,
                  { latitude: navigating.latitude, longitude: navigating.longitude }
                ]}
                strokeColor="#3B82F6"
                strokeWidth={5}
                lineCap="round"
                lineJoin="round"
              />
            )}
          </MapView>

          <View style={styles.mapLegend}>
            <View style={styles.mapLegendDot} />
            <Text style={styles.mapLegendText}>You are here</Text>
          </View>

          {!navigating && (
            <TouchableOpacity 
              style={styles.mapResetBtn}
              onPress={() => mapRef.current?.animateToRegion(AIRPORT_CENTER, 300)}
            >
              <Text style={styles.mapResetText}>↻</Text>
            </TouchableOpacity>
          )}

          {navigating && (
            <View style={styles.navPanel}>
              <View style={styles.navPanelHeader}>
                <View style={[styles.navPanelIcon, { backgroundColor: TYPE_COLORS[navigating.type] }]}>
                  <Text style={styles.navPanelEmoji}>{TYPE_ICONS[navigating.type]}</Text>
                </View>
                <View style={styles.navPanelInfo}>
                  <Text style={styles.navPanelLabel}>Navigating to</Text>
                  <Text style={styles.navPanelTitle}>{navigating.name}</Text>
                </View>
                <TouchableOpacity style={styles.navPanelClose} onPress={stopNav}>
                  <Text style={styles.navPanelCloseText}>✕</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.navPanelStats}>
                <View style={styles.navPanelStat}>
                  <Text style={styles.navPanelStatValue}>{formatDistance(calcDistance(navigating))}</Text>
                  <Text style={styles.navPanelStatLabel}>Distance</Text>
                </View>
                <View style={styles.navPanelStatDivider} />
                <View style={styles.navPanelStat}>
                  <Text style={styles.navPanelStatValue}>{calcWalkTime(calcDistance(navigating))} min</Text>
                  <Text style={styles.navPanelStatLabel}>Walk time</Text>
                </View>
              </View>

              <View style={styles.navPanelTip}>
                <Text style={styles.navPanelTipText}>🚶 Follow the blue line on the map</Text>
              </View>
            </View>
          )}
        </View>
      ) : (
        <FlatList
          data={sortedPOIs}
          keyExtractor={item => item.id}
          renderItem={renderListItem}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* Detail Modal */}
      <Modal
        visible={selectedPOI !== null}
        transparent
        animationType="slide"
        onRequestClose={() => setSelectedPOI(null)}
      >
        <View style={styles.modalOverlay}>
          <TouchableOpacity 
            style={styles.modalBackdrop} 
            activeOpacity={1}
            onPress={() => setSelectedPOI(null)} 
          />
          
          {selectedPOI && (
            <View style={styles.modalSheet}>
              <View style={styles.modalHandle} />
              
              <View style={styles.modalHeader}>
                <View style={[styles.modalIcon, { backgroundColor: TYPE_COLORS[selectedPOI.type] }]}>
                  <Text style={styles.modalEmoji}>{TYPE_ICONS[selectedPOI.type]}</Text>
                </View>
                <View style={styles.modalHeaderInfo}>
                  <Text style={styles.modalTitle}>{selectedPOI.name}</Text>
                  <Text style={[styles.modalType, { color: TYPE_COLORS[selectedPOI.type] }]}>
                    {selectedPOI.type.charAt(0).toUpperCase() + selectedPOI.type.slice(1)}
                  </Text>
                </View>
              </View>

              <View style={styles.modalStats}>
                <View style={styles.modalStat}>
                  <Text style={styles.modalStatValue}>{formatDistance(calcDistance(selectedPOI))}</Text>
                  <Text style={styles.modalStatLabel}>Distance</Text>
                </View>
                <View style={styles.modalStat}>
                  <Text style={styles.modalStatValue}>{calcWalkTime(calcDistance(selectedPOI))} min</Text>
                  <Text style={styles.modalStatLabel}>Walk time</Text>
                </View>
              </View>

              {selectedPOI.description && (
                <Text style={styles.modalDesc}>{selectedPOI.description}</Text>
              )}

              <TouchableOpacity
                style={[styles.modalNavBtn, { backgroundColor: TYPE_COLORS[selectedPOI.type] }]}
                onPress={() => startNav(selectedPOI)}
              >
                <Text style={styles.modalNavBtnText}>🧭 Start Navigation</Text>
              </TouchableOpacity>

              <TouchableOpacity 
                style={styles.modalCancelBtn}
                onPress={() => setSelectedPOI(null)}
              >
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },

  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
  },
  headerSub: {
    fontSize: 12,
    color: '#94A3B8',
    fontWeight: '500',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 2,
  },
  headerToggle: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerToggleText: {
    fontSize: 20,
  },

  // Quick Actions
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  quickBtn: {
    alignItems: 'center',
  },
  quickBtnIcon: {
    width: 52,
    height: 52,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 6,
  },
  quickBtnEmoji: {
    fontSize: 24,
  },
  quickBtnLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '500',
  },

  // Filter
  filterWrapper: {
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  filterContainer: {
    paddingLeft: 16,
    paddingRight: 24,
    paddingVertical: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#F1F5F9',
    marginRight: 8,
  },
  filterChipActive: {
    backgroundColor: '#1E293B',
  },
  filterChipText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  filterChipTextActive: {
    color: '#FFFFFF',
  },

  // List
  listContent: {
    padding: 16,
  },
  listCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 12,
    marginBottom: 10,
  },
  listCardIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  listCardEmoji: {
    fontSize: 22,
  },
  listCardContent: {
    flex: 1,
    marginLeft: 12,
  },
  listCardTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1E293B',
  },
  listCardSubtitle: {
    fontSize: 13,
    color: '#94A3B8',
    marginTop: 2,
  },
  listCardButton: {
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 10,
  },
  listCardButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },

  // Map
  mapContainer: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  mapLegend: {
    position: 'absolute',
    top: 12,
    left: 12,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  mapLegendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#EF4444',
    marginRight: 8,
  },
  mapLegendText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1E293B',
  },
  mapResetBtn: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  mapResetText: {
    fontSize: 22,
    color: '#1E293B',
  },

  // Navigation Panel
  navPanel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 32,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  navPanelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  navPanelIcon: {
    width: 50,
    height: 50,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  navPanelEmoji: {
    fontSize: 24,
  },
  navPanelInfo: {
    flex: 1,
    marginLeft: 12,
  },
  navPanelLabel: {
    fontSize: 12,
    color: '#94A3B8',
    fontWeight: '500',
  },
  navPanelTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 2,
  },
  navPanelClose: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  navPanelCloseText: {
    fontSize: 16,
    color: '#64748B',
  },
  navPanelStats: {
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
  },
  navPanelStat: {
    flex: 1,
    alignItems: 'center',
  },
  navPanelStatDivider: {
    width: 1,
    backgroundColor: '#E2E8F0',
    marginHorizontal: 10,
  },
  navPanelStatValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1E293B',
  },
  navPanelStatLabel: {
    fontSize: 12,
    color: '#94A3B8',
    marginTop: 4,
  },
  navPanelTip: {
    backgroundColor: '#EFF6FF',
    borderRadius: 12,
    padding: 14,
  },
  navPanelTipText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '600',
    textAlign: 'center',
  },

  // Modal
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  modalBackdrop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
  },
  modalSheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 32,
  },
  modalHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#E2E8F0',
    alignSelf: 'center',
    marginBottom: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalEmoji: {
    fontSize: 28,
  },
  modalHeaderInfo: {
    flex: 1,
    marginLeft: 14,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1E293B',
  },
  modalType: {
    fontSize: 14,
    fontWeight: '600',
    marginTop: 4,
  },
  modalStats: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  modalStat: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
    marginRight: 10,
  },
  modalStatValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1E293B',
  },
  modalStatLabel: {
    fontSize: 12,
    color: '#94A3B8',
    marginTop: 4,
  },
  modalDesc: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
    marginBottom: 20,
  },
  modalNavBtn: {
    paddingVertical: 16,
    borderRadius: 14,
    alignItems: 'center',
    marginBottom: 12,
  },
  modalNavBtnText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  modalCancelBtn: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  modalCancelText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#94A3B8',
  },
});
