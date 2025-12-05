import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  FlatList,
} from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';

interface MapScreenProps {
  showHeader?: boolean;
}

interface Location {
  id: string;
  name: string;
  level: string;
  category: string;
  x: number;
  y: number;
  icon: string;
  color: string;
  details: string;
}

interface Category {
  id: string;
  label: string;
  icon: string;
  color: string;
}

const locations: Location[] = [
  // Level 2 - Departures
  {id: '1', name: 'Gate 1', level: '2', category: 'gate', x: 88, y: 22, icon: 'plane', color: '#1a5f7a', details: 'Domestic Flights • Near Exit'},
  {id: '2', name: 'Gate 5', level: '2', category: 'gate', x: 73, y: 22, icon: 'plane', color: '#1a5f7a', details: 'Domestic Flights'},
  {id: '3', name: 'Gate 10', level: '2', category: 'gate', x: 58, y: 22, icon: 'plane', color: '#1a5f7a', details: 'US Departures'},
  {id: '4', name: 'Gate 14', level: '2', category: 'gate', x: 43, y: 22, icon: 'plane', color: '#1a5f7a', details: 'International Flights'},
  {id: '5', name: 'Gate 20', level: '2', category: 'gate', x: 28, y: 22, icon: 'plane', color: '#1a5f7a', details: 'International Flights'},
  // Restaurants with brand colors
  {id: '6', name: 'Tim Hortons', level: '2', category: 'restaurant', x: 72, y: 58, icon: 'coffee', color: '#c8102e', details: 'Coffee, Donuts & Snacks'},
  {id: '7', name: 'Starbucks', level: '2', category: 'restaurant', x: 42, y: 58, icon: 'coffee', color: '#00704a', details: 'Coffee & Pastries'},
  {id: '8', name: 'The Alehouse', level: '2', category: 'restaurant', x: 57, y: 58, icon: 'glass', color: '#8b4513', details: 'Bar & Grill'},
  // Shops with brand colors
  {id: '9', name: 'Duty Free', level: '2', category: 'shop', x: 32, y: 78, icon: 'shopping-bag', color: '#e91e63', details: 'Tax-Free Shopping'},
  {id: '10', name: 'Hudson News', level: '2', category: 'shop', x: 78, y: 78, icon: 'book', color: '#ff6600', details: 'Books & Magazines'},
  {id: '11', name: 'Restrooms', level: '2', category: 'restroom', x: 55, y: 78, icon: 'users', color: '#2980b9', details: 'Main Hall'},
  {id: '12', name: 'Restrooms', level: '2', category: 'restroom', x: 92, y: 55, icon: 'users', color: '#2980b9', details: 'East Wing'},
  {id: '13', name: 'Charging', level: '2', category: 'charging', x: 65, y: 78, icon: 'bolt', color: '#f39c12', details: 'Free USB & Outlets'},
  {id: '14', name: 'Security', level: '2', category: 'gate', x: 15, y: 58, icon: 'shield', color: '#1a5f7a', details: 'Security Checkpoint'},

  // Level 1 - Arrivals  
  {id: '15', name: 'Check-in A', level: '1', category: 'gate', x: 25, y: 25, icon: 'check-square-o', color: '#1a5f7a', details: 'Air Canada, WestJet'},
  {id: '16', name: 'Check-in B', level: '1', category: 'gate', x: 50, y: 25, icon: 'check-square-o', color: '#1a5f7a', details: 'International'},
  {id: '17', name: 'Check-in C', level: '1', category: 'gate', x: 75, y: 25, icon: 'check-square-o', color: '#1a5f7a', details: 'US Airlines'},
  {id: '18', name: 'Baggage 1-3', level: '1', category: 'gate', x: 30, y: 75, icon: 'suitcase', color: '#1a5f7a', details: 'Domestic'},
  {id: '19', name: 'Baggage 4-6', level: '1', category: 'gate', x: 70, y: 75, icon: 'suitcase', color: '#1a5f7a', details: 'International'},
  {id: '20', name: 'Tim Hortons', level: '1', category: 'restaurant', x: 40, y: 50, icon: 'coffee', color: '#c8102e', details: 'Coffee & Donuts'},
  {id: '21', name: 'Subway', level: '1', category: 'restaurant', x: 60, y: 50, icon: 'cutlery', color: '#009743', details: 'Fresh Sandwiches'},
  {id: '22', name: 'Gift Shop', level: '1', category: 'shop', x: 85, y: 50, icon: 'gift', color: '#9c27b0', details: 'Souvenirs'},
  {id: '23', name: 'Exchange', level: '1', category: 'shop', x: 15, y: 50, icon: 'money', color: '#2196f3', details: 'Currency'},
  {id: '24', name: 'Restrooms', level: '1', category: 'restroom', x: 50, y: 50, icon: 'users', color: '#2980b9', details: 'Central'},
  {id: '25', name: 'Info Desk', level: '1', category: 'gate', x: 50, y: 38, icon: 'info-circle', color: '#1a5f7a', details: 'Help'},

  // Ground Level
  {id: '26', name: 'Parking P1', level: 'LL', category: 'gate', x: 20, y: 30, icon: 'car', color: '#1a5f7a', details: 'Short-term'},
  {id: '27', name: 'Parking P2', level: 'LL', category: 'gate', x: 50, y: 30, icon: 'car', color: '#1a5f7a', details: 'Long-term'},
  {id: '28', name: 'Parking P3', level: 'LL', category: 'gate', x: 80, y: 30, icon: 'car', color: '#1a5f7a', details: 'Economy'},
  {id: '29', name: 'Taxi', level: 'LL', category: 'gate', x: 25, y: 70, icon: 'taxi', color: '#f39c12', details: 'Taxi Stand'},
  {id: '30', name: 'Bus', level: 'LL', category: 'gate', x: 50, y: 70, icon: 'bus', color: '#3498db', details: 'Route 320'},
  {id: '31', name: 'Rideshare', level: 'LL', category: 'gate', x: 75, y: 70, icon: 'automobile', color: '#000', details: 'Uber/Lyft'},
  {id: '32', name: 'Car Rentals', level: 'LL', category: 'shop', x: 88, y: 50, icon: 'car', color: '#ffd900', details: 'Hertz, Avis, Enterprise'},
  {id: '33', name: 'Restrooms', level: 'LL', category: 'restroom', x: 50, y: 85, icon: 'users', color: '#2980b9', details: 'Ground'},
];

const categories: Category[] = [
  {id: 'gate', label: 'Gates', icon: 'plane', color: '#1a5f7a'},
  {id: 'restaurant', label: 'Food', icon: 'cutlery', color: '#c0392b'},
  {id: 'shop', label: 'Shops', icon: 'shopping-bag', color: '#8e44ad'},
  {id: 'restroom', label: 'Restrooms', icon: 'users', color: '#2980b9'},
  {id: 'charging', label: 'Charging', icon: 'bolt', color: '#f39c12'},
];

const MapScreen: React.FC<MapScreenProps> = ({showHeader: _showHeader = true}) => {
  const [selectedLevel, setSelectedLevel] = useState<string>('2');
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const filteredLocations = locations.filter(
    loc => loc.level === selectedLevel && (selectedCategory === null || loc.category === selectedCategory),
  );

  const getLevelInfo = (level: string) => {
    switch (level) {
      case '2': return {name: 'Level 2', desc: 'Departures', color: '#e74c3c'};
      case '1': return {name: 'Level 1', desc: 'Arrivals', color: '#27ae60'};
      case 'LL': return {name: 'Ground', desc: 'Transport', color: '#3498db'};
      default: return {name: '', desc: '', color: '#666'};
    }
  };

  const getIcon = (name: string): string => {
    const map: {[k: string]: string} = {
      plane: 'plane', coffee: 'coffee', glass: 'glass', bolt: 'bolt',
      'shopping-bag': 'shopping-bag', book: 'book', users: 'users',
      suitcase: 'suitcase', cutlery: 'cutlery', gift: 'gift',
      money: 'money', car: 'car', taxi: 'taxi', bus: 'bus',
      'check-square-o': 'check-square-o', 'info-circle': 'info-circle',
      shield: 'shield', automobile: 'automobile',
    };
    return map[name] || 'map-marker';
  };

  const renderLocationTile = ({item}: {item: Location}) => {
    const isSelected = selectedLocation?.id === item.id;
    return (
      <TouchableOpacity
        style={[styles.tile, isSelected && styles.tileSelected]}
        onPress={() => setSelectedLocation(item)}
        activeOpacity={0.7}>
        <View style={[styles.tileIcon, {backgroundColor: item.color}]}>
          <FontAwesome name={getIcon(item.icon)} size={18} color="#fff" />
        </View>
        <View style={styles.tileContent}>
          <Text style={styles.tileName} numberOfLines={1}>{item.name}</Text>
          <Text style={styles.tileDetails} numberOfLines={1}>{item.details}</Text>
        </View>
        <FontAwesome name="chevron-right" size={12} color="#ccc" />
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {/* Level Selector */}
      <View style={styles.levelBar}>
        {['2', '1', 'LL'].map(level => {
          const info = getLevelInfo(level);
          const isActive = selectedLevel === level;
          return (
            <TouchableOpacity
              key={level}
              style={[styles.levelBtn, isActive && styles.levelBtnActive]}
              onPress={() => {
                setSelectedLevel(level);
                setSelectedLocation(null);
              }}>
              <View style={[styles.levelDot, {backgroundColor: info.color}]} />
              <View>
                <Text style={[styles.levelName, isActive && styles.levelNameActive]}>{info.name}</Text>
                <Text style={[styles.levelDesc, isActive && styles.levelDescActive]}>{info.desc}</Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Category Filter */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.catScroll} contentContainerStyle={styles.catContent}>
        <TouchableOpacity
          style={[styles.catPill, !selectedCategory && styles.catPillActive]}
          onPress={() => setSelectedCategory(null)}>
          <Text style={[styles.catText, !selectedCategory && styles.catTextActive]}>All</Text>
        </TouchableOpacity>
        {categories.map(cat => (
          <TouchableOpacity
            key={cat.id}
            style={[styles.catPill, selectedCategory === cat.id && {backgroundColor: cat.color}]}
            onPress={() => setSelectedCategory(selectedCategory === cat.id ? null : cat.id)}>
            <FontAwesome name={getIcon(cat.icon)} size={12} color={selectedCategory === cat.id ? '#fff' : cat.color} />
            <Text style={[styles.catText, selectedCategory === cat.id && styles.catTextActive]}>{cat.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* FLOOR PLAN MAP */}
      <View style={styles.mapArea}>
        <View style={styles.floorPlan}>
          
          {/* ===== LEVEL 2 - DEPARTURES ===== */}
          {selectedLevel === '2' && (
            <>
              <View style={styles.mapBackground} />
              
              {/* Gate Concourse */}
              <View style={styles.gateConcourse}>
                <Text style={styles.zoneTitle}>GATE CONCOURSE</Text>
                <View style={styles.gateRow}>
                  <View style={styles.gateBox}><Text style={styles.gateLabel}>20</Text></View>
                  <View style={styles.gateBox}><Text style={styles.gateLabel}>14</Text></View>
                  <View style={styles.gateBox}><Text style={styles.gateLabel}>10</Text></View>
                  <View style={styles.gateBox}><Text style={styles.gateLabel}>5</Text></View>
                  <View style={styles.gateBox}><Text style={styles.gateLabel}>1</Text></View>
                </View>
              </View>
              
              {/* Main Corridor */}
              <View style={styles.mainCorridor}>
                <View style={styles.corridorPath} />
              </View>
              
              {/* Food & Shopping Area */}
              <View style={styles.serviceArea}>
                <View style={styles.serviceZone}>
                  <Text style={styles.zoneLabel}>🛡️ SECURITY</Text>
                </View>
                <View style={[styles.serviceZone, styles.diningZone]}>
                  <Text style={styles.zoneLabel}>🍽️ DINING</Text>
                </View>
                <View style={[styles.serviceZone, styles.shopsZone]}>
                  <Text style={styles.zoneLabel}>🛍️ SHOPS</Text>
                </View>
              </View>
              
              {/* Entrance */}
              <View style={styles.entranceArea}>
                <Text style={styles.entranceText}>← TO ARRIVALS</Text>
              </View>
            </>
          )}

          {/* ===== LEVEL 1 - ARRIVALS ===== */}
          {selectedLevel === '1' && (
            <>
              <View style={styles.mapBackground} />
              
              {/* Check-in Area */}
              <View style={styles.checkinArea}>
                <Text style={styles.zoneTitle}>CHECK-IN COUNTERS</Text>
                <View style={styles.counterRow}>
                  <View style={styles.counterDesk}><Text style={styles.counterLabel}>A</Text></View>
                  <View style={styles.counterDesk}><Text style={styles.counterLabel}>B</Text></View>
                  <View style={styles.counterDesk}><Text style={styles.counterLabel}>C</Text></View>
                </View>
              </View>
              
              {/* Main Hall */}
              <View style={styles.mainHall}>
                <View style={styles.hallPath} />
                <Text style={styles.hallLabel}>MAIN HALL</Text>
              </View>
              
              {/* Services */}
              <View style={styles.arrivalServices}>
                <View style={styles.serviceBox}>
                  <Text style={styles.serviceLabel}>💱</Text>
                </View>
                <View style={styles.serviceBox}>
                  <Text style={styles.serviceLabel}>🍽️</Text>
                </View>
                <View style={styles.serviceBox}>
                  <Text style={styles.serviceLabel}>ℹ️</Text>
                </View>
                <View style={styles.serviceBox}>
                  <Text style={styles.serviceLabel}>🛍️</Text>
                </View>
              </View>
              
              {/* Baggage Claim */}
              <View style={styles.baggageArea}>
                <Text style={styles.zoneTitle}>BAGGAGE CLAIM</Text>
                <View style={styles.carouselRow}>
                  <View style={styles.carouselItem}><Text style={styles.carouselLabel}>1-3</Text></View>
                  <View style={styles.carouselItem}><Text style={styles.carouselLabel}>4-6</Text></View>
                </View>
              </View>
              
              {/* Exit */}
              <View style={styles.exitArea}>
                <Text style={styles.exitText}>EXIT → GROUND TRANSPORT</Text>
              </View>
            </>
          )}

          {/* ===== GROUND LEVEL ===== */}
          {selectedLevel === 'LL' && (
            <>
              <View style={styles.mapBackground} />
              
              {/* Parking */}
              <View style={styles.parkingSection}>
                <Text style={styles.zoneTitle}>PARKING</Text>
                <View style={styles.parkingRow}>
                  <View style={styles.parkingBox}>
                    <FontAwesome name="car" size={16} color="#1a5f7a" />
                    <Text style={styles.parkingLabel}>P1</Text>
                    <Text style={styles.parkingType}>Short</Text>
                  </View>
                  <View style={styles.parkingBox}>
                    <FontAwesome name="car" size={16} color="#1a5f7a" />
                    <Text style={styles.parkingLabel}>P2</Text>
                    <Text style={styles.parkingType}>Long</Text>
                  </View>
                  <View style={styles.parkingBox}>
                    <FontAwesome name="car" size={16} color="#1a5f7a" />
                    <Text style={styles.parkingLabel}>P3</Text>
                    <Text style={styles.parkingType}>Economy</Text>
                  </View>
                </View>
              </View>
              
              {/* Road */}
              <View style={styles.roadSection}>
                <View style={styles.road}>
                  <View style={styles.roadLine} />
                </View>
                <Text style={styles.roadLabel}>ACCESS ROAD</Text>
              </View>
              
              {/* Pickup Zone */}
              <View style={styles.pickupSection}>
                <Text style={styles.zoneTitle}>PICKUP / DROP-OFF</Text>
                <View style={styles.pickupRow}>
                  <View style={styles.pickupBox}>
                    <FontAwesome name="taxi" size={20} color="#f39c12" />
                    <Text style={styles.pickupLabel}>TAXI</Text>
                  </View>
                  <View style={styles.pickupBox}>
                    <FontAwesome name="bus" size={20} color="#3498db" />
                    <Text style={styles.pickupLabel}>BUS</Text>
                  </View>
                  <View style={styles.pickupBox}>
                    <FontAwesome name="automobile" size={20} color="#000" />
                    <Text style={styles.pickupLabel}>RIDESHARE</Text>
                  </View>
                </View>
              </View>
              
              {/* Terminal Entrance */}
              <View style={styles.terminalLink}>
                <Text style={styles.terminalLinkText}>↑ TERMINAL ENTRANCE</Text>
              </View>
            </>
          )}

          {/* Location Markers */}
          {filteredLocations.map(loc => {
            const isSelected = selectedLocation?.id === loc.id;
            return (
              <TouchableOpacity
                key={loc.id}
                style={[
                  styles.marker,
                  {left: `${loc.x}%`, top: `${loc.y}%`, backgroundColor: loc.color},
                  isSelected && styles.markerSelected,
                ]}
                onPress={() => setSelectedLocation(loc)}>
                <FontAwesome name={getIcon(loc.icon)} size={12} color="#fff" />
                {isSelected && (
                  <View style={styles.markerTooltip}>
                    <Text style={styles.markerTooltipText}>{loc.name}</Text>
                  </View>
                )}
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Map Legend */}
        <View style={styles.mapLegend}>
          {categories.map(cat => (
            <View key={cat.id} style={styles.legendItem}>
              <View style={[styles.legendDot, {backgroundColor: cat.color}]} />
              <Text style={styles.legendText}>{cat.label}</Text>
            </View>
          ))}
        </View>
        
        {/* Level Badge */}
        <View style={[styles.levelBadge, {backgroundColor: getLevelInfo(selectedLevel).color}]}>
          <Text style={styles.levelBadgeText}>{getLevelInfo(selectedLevel).desc}</Text>
        </View>
      </View>

      {/* LOCATIONS LIST */}
      <View style={styles.listSection}>
        <View style={styles.listHeader}>
          <Text style={styles.listTitle}>
            {selectedCategory ? categories.find(c => c.id === selectedCategory)?.label : 'All Locations'}
          </Text>
          <Text style={styles.listCount}>{filteredLocations.length} found</Text>
        </View>
        <FlatList
          data={filteredLocations}
          keyExtractor={item => item.id}
          renderItem={renderLocationTile}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContent}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f5f6f8'},
  
  // Level Bar
  levelBar: {flexDirection: 'row', backgroundColor: '#fff', padding: 8, gap: 6, borderBottomWidth: 1, borderBottomColor: '#eee'},
  levelBtn: {flex: 1, flexDirection: 'row', alignItems: 'center', padding: 10, borderRadius: 10, backgroundColor: '#f5f5f5', gap: 8},
  levelBtnActive: {backgroundColor: '#0C2340'},
  levelDot: {width: 8, height: 8, borderRadius: 4},
  levelName: {fontSize: 13, fontWeight: '700', color: '#333'},
  levelNameActive: {color: '#fff'},
  levelDesc: {fontSize: 10, color: '#888', marginTop: 1},
  levelDescActive: {color: '#FFD100'},

  // Category
  catScroll: {backgroundColor: '#fff', maxHeight: 48, borderBottomWidth: 1, borderBottomColor: '#eee'},
  catContent: {paddingHorizontal: 10, paddingVertical: 8, gap: 8, flexDirection: 'row', alignItems: 'center'},
  catPill: {flexDirection: 'row', alignItems: 'center', paddingVertical: 6, paddingHorizontal: 14, borderRadius: 16, backgroundColor: '#f0f0f0', gap: 6},
  catPillActive: {backgroundColor: '#0C2340'},
  catText: {fontSize: 12, fontWeight: '600', color: '#555'},
  catTextActive: {color: '#FFD100'},

  // Map Area
  mapArea: {height: 300, position: 'relative', backgroundColor: '#e8eff5'},
  floorPlan: {flex: 1, margin: 10, backgroundColor: '#fff', borderRadius: 12, position: 'relative', overflow: 'hidden', borderWidth: 1, borderColor: '#ddd'},
  mapBackground: {position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#f8fafc'},

  // Level 2 - Departures
  gateConcourse: {position: 'absolute', top: 8, left: 15, right: 15, height: 55, backgroundColor: '#e3f2fd', borderRadius: 8, padding: 6, alignItems: 'center'},
  zoneTitle: {fontSize: 8, fontWeight: '700', color: '#1565c0', letterSpacing: 0.5, marginBottom: 4},
  gateRow: {flexDirection: 'row', justifyContent: 'space-around', flex: 1, width: '100%'},
  gateBox: {width: 32, height: 28, backgroundColor: '#1a5f7a', borderRadius: 4, justifyContent: 'center', alignItems: 'center'},
  gateLabel: {fontSize: 11, fontWeight: 'bold', color: '#fff'},
  
  mainCorridor: {position: 'absolute', top: 68, left: 20, right: 20, height: 20, justifyContent: 'center'},
  corridorPath: {height: 8, backgroundColor: '#eceff1', borderRadius: 4},
  
  serviceArea: {position: 'absolute', top: 95, left: 15, right: 15, height: 55, flexDirection: 'row', gap: 8},
  serviceZone: {flex: 1, backgroundColor: '#e8f5e9', borderRadius: 8, justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: '#c8e6c9'},
  diningZone: {backgroundColor: '#ffebee', borderColor: '#ffcdd2'},
  shopsZone: {backgroundColor: '#f3e5f5', borderColor: '#e1bee7'},
  zoneLabel: {fontSize: 9, fontWeight: '600', color: '#333'},
  
  entranceArea: {position: 'absolute', bottom: 10, left: 15, right: 15, height: 30, backgroundColor: '#e8f5e9', borderRadius: 6, justifyContent: 'center', alignItems: 'center'},
  entranceText: {fontSize: 10, fontWeight: '600', color: '#2e7d32'},

  // Level 1 - Arrivals
  checkinArea: {position: 'absolute', top: 8, left: 15, right: 15, height: 60, backgroundColor: '#e8f5e9', borderRadius: 8, padding: 6, alignItems: 'center'},
  counterRow: {flexDirection: 'row', justifyContent: 'space-around', flex: 1, width: '100%'},
  counterDesk: {width: 50, height: 30, backgroundColor: '#43a047', borderRadius: 4, justifyContent: 'center', alignItems: 'center'},
  counterLabel: {fontSize: 14, fontWeight: 'bold', color: '#fff'},
  
  mainHall: {position: 'absolute', top: 75, left: 20, right: 20, height: 30, justifyContent: 'center', alignItems: 'center'},
  hallPath: {position: 'absolute', top: 12, left: 0, right: 0, height: 6, backgroundColor: '#eceff1', borderRadius: 3},
  hallLabel: {fontSize: 9, fontWeight: '600', color: '#78909c', backgroundColor: '#fff', paddingHorizontal: 8},
  
  arrivalServices: {position: 'absolute', top: 110, left: 15, right: 15, height: 40, flexDirection: 'row', gap: 8},
  serviceBox: {flex: 1, backgroundColor: '#fce4ec', borderRadius: 6, justifyContent: 'center', alignItems: 'center'},
  serviceLabel: {fontSize: 16},
  
  baggageArea: {position: 'absolute', bottom: 35, left: 15, right: 15, height: 55, backgroundColor: '#e3f2fd', borderRadius: 8, padding: 6, alignItems: 'center'},
  carouselRow: {flexDirection: 'row', justifyContent: 'space-around', flex: 1, width: '100%'},
  carouselItem: {width: 60, height: 28, backgroundColor: '#1976d2', borderRadius: 14, justifyContent: 'center', alignItems: 'center'},
  carouselLabel: {fontSize: 12, fontWeight: 'bold', color: '#fff'},
  
  exitArea: {position: 'absolute', bottom: 8, left: 15, right: 15, height: 22, backgroundColor: '#fff3e0', borderRadius: 4, justifyContent: 'center', alignItems: 'center'},
  exitText: {fontSize: 9, fontWeight: '600', color: '#e65100'},

  // Ground Level
  parkingSection: {position: 'absolute', top: 8, left: 15, right: 15, height: 75, backgroundColor: '#eceff1', borderRadius: 8, padding: 6, alignItems: 'center'},
  parkingRow: {flexDirection: 'row', justifyContent: 'space-around', flex: 1, width: '100%'},
  parkingBox: {width: 70, height: 50, backgroundColor: '#fff', borderRadius: 6, justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderStyle: 'dashed', borderColor: '#90a4ae'},
  parkingLabel: {fontSize: 14, fontWeight: 'bold', color: '#37474f'},
  parkingType: {fontSize: 8, color: '#78909c'},
  
  roadSection: {position: 'absolute', top: 95, left: 15, right: 15, height: 35, alignItems: 'center'},
  road: {width: '100%', height: 20, backgroundColor: '#455a64', borderRadius: 2, justifyContent: 'center'},
  roadLine: {height: 2, backgroundColor: '#ffd54f', marginHorizontal: 20},
  roadLabel: {fontSize: 8, fontWeight: '600', color: '#78909c', marginTop: 2},
  
  pickupSection: {position: 'absolute', bottom: 35, left: 15, right: 15, height: 70, backgroundColor: '#e8f5e9', borderRadius: 8, padding: 6, alignItems: 'center'},
  pickupRow: {flexDirection: 'row', justifyContent: 'space-around', flex: 1, width: '100%'},
  pickupBox: {width: 70, height: 45, backgroundColor: '#fff', borderRadius: 8, justifyContent: 'center', alignItems: 'center', gap: 2},
  pickupLabel: {fontSize: 8, fontWeight: '700', color: '#2e7d32'},
  
  terminalLink: {position: 'absolute', bottom: 8, left: 15, right: 15, height: 22, backgroundColor: '#e3f2fd', borderRadius: 4, justifyContent: 'center', alignItems: 'center'},
  terminalLinkText: {fontSize: 9, fontWeight: '600', color: '#1565c0'},

  // Markers
  marker: {
    position: 'absolute',
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#fff',
    marginLeft: -14,
    marginTop: -14,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.3,
    shadowRadius: 3,
  },
  markerSelected: {
    borderColor: '#FFD100',
    borderWidth: 3,
    transform: [{scale: 1.25}],
    zIndex: 100,
  },
  markerTooltip: {
    position: 'absolute',
    top: -30,
    backgroundColor: '#0C2340',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    minWidth: 60,
  },
  markerTooltipText: {fontSize: 9, color: '#fff', fontWeight: '600', textAlign: 'center'},

  // Legend & Badge
  mapLegend: {position: 'absolute', bottom: 18, left: 18, backgroundColor: 'rgba(255,255,255,0.95)', borderRadius: 8, padding: 8, flexDirection: 'row', gap: 12, elevation: 2},
  legendItem: {flexDirection: 'row', alignItems: 'center', gap: 4},
  legendDot: {width: 10, height: 10, borderRadius: 5},
  legendText: {fontSize: 10, color: '#333', fontWeight: '500'},
  
  levelBadge: {position: 'absolute', top: 18, right: 18, paddingHorizontal: 14, paddingVertical: 6, borderRadius: 14, elevation: 2},
  levelBadgeText: {fontSize: 11, color: '#fff', fontWeight: '700'},

  // List Section
  listSection: {flex: 1, backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20, marginTop: -10, paddingTop: 6, elevation: 8, shadowColor: '#000', shadowOffset: {width: 0, height: -3}, shadowOpacity: 0.1, shadowRadius: 6},
  listHeader: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#f0f0f0'},
  listTitle: {fontSize: 16, fontWeight: '700', color: '#0C2340'},
  listCount: {fontSize: 12, color: '#888', fontWeight: '500'},
  listContent: {paddingHorizontal: 12, paddingBottom: 20},

  tile: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    marginTop: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#f0f0f0',
    gap: 12,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  tileSelected: {
    borderColor: '#FFD100',
    borderWidth: 2,
    backgroundColor: '#FFFDF0',
  },
  tileIcon: {width: 42, height: 42, borderRadius: 21, alignItems: 'center', justifyContent: 'center'},
  tileContent: {flex: 1},
  tileName: {fontSize: 14, fontWeight: '600', color: '#0C2340'},
  tileDetails: {fontSize: 11, color: '#888', marginTop: 2},
});

export default MapScreen;