import React, { useState } from 'react';
import { ScrollView, StyleSheet, Text, View, TouchableOpacity, StatusBar } from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';

// Mock flight data
const mockFlights = [
  {
    id: '1',
    flightNumber: 'AA1234',
    from: 'NYC',
    to: 'LAX',
    departure: '08:30',
    arrival: '11:45',
    status: 'On Time',
    gate: 'A12',
    type: 'departure',
  },
  {
    id: '2',
    flightNumber: 'DL5678',
    from: 'LAX',
    to: 'CHI',
    departure: '14:20',
    arrival: '18:35',
    status: 'Delayed',
    gate: 'B8',
    type: 'arrival',
  },
  {
    id: '3',
    flightNumber: 'UA9012',
    from: 'CHI',
    to: 'MIA',
    departure: '16:45',
    arrival: '20:15',
    status: 'On Time',
    gate: 'C15',
    type: 'departure',
  },
  {
    id: '4',
    flightNumber: 'SW3456',
    from: 'MIA',
    to: 'DEN',
    departure: '09:15',
    arrival: '12:30',
    status: 'Boarding',
    gate: 'D22',
    type: 'arrival',
  },
  {
    id: '5',
    flightNumber: 'JB7890',
    from: 'DEN',
    to: 'SEA',
    departure: '13:00',
    arrival: '15:20',
    status: 'On Time',
    gate: 'E5',
    type: 'departure',
  },
  {
    id: '6',
    flightNumber: 'BA4567',
    from: 'SEA',
    to: 'NYC',
    departure: '19:00',
    arrival: '03:15',
    status: 'On Time',
    gate: 'F9',
    type: 'arrival',
  },
];

interface GuestFlightsScreenProps {
  onBack: () => void;
}

export default function GuestFlightsScreen({ onBack }: GuestFlightsScreenProps) {
  const [activeTab, setActiveTab] = useState<'departure' | 'arrival'>('departure');
  
  const departures = mockFlights.filter(f => f.type === 'departure');
  const arrivals = mockFlights.filter(f => f.type === 'arrival');

  const currentFlights = activeTab === 'departure' ? departures : arrivals;

  const handleBack = () => {
    onBack();
  };

  const renderFlightCard = (flight: typeof mockFlights[0]) => (
    <View key={flight.id} style={styles.flightCard}>
      <View style={styles.flightHeader}>
        <Text style={styles.flightNumber}>{flight.flightNumber}</Text>
        <Text style={[
          styles.status,
          flight.status === 'Delayed' && styles.delayedStatus,
          flight.status === 'Boarding' && styles.boardingStatus
        ]}>
          {flight.status}
        </Text>
      </View>
      
      <View style={styles.routeContainer}>
        <View style={styles.airportInfo}>
          <Text style={styles.airportCode}>{flight.from}</Text>
          <Text style={styles.time}>{flight.departure}</Text>
        </View>
        
        <View style={styles.flightPath}>
          <FontAwesome name="plane" size={16} color="#666" />
          <View style={styles.pathLine} />
        </View>
        
        <View style={styles.airportInfo}>
          <Text style={styles.airportCode}>{flight.to}</Text>
          <Text style={styles.time}>{flight.arrival}</Text>
        </View>
      </View>
      
      <Text style={styles.gate}>Gate: {flight.gate}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0C2340" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={handleBack} style={styles.backButton}>
          <FontAwesome name="arrow-left" size={20} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Flight Information</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Tab Buttons */}
      <View style={styles.tabContainer}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'departure' && styles.activeTab]}
          onPress={() => setActiveTab('departure')}
        >
          <FontAwesome 
            name="plane" 
            size={18} 
            color={activeTab === 'departure' ? '#0C2340' : '#999'} 
          />
          <Text style={[styles.tabText, activeTab === 'departure' && styles.activeTabText]}>
            Departures
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tab, activeTab === 'arrival' && styles.activeTab]}
          onPress={() => setActiveTab('arrival')}
        >
          <FontAwesome 
            name="plane" 
            size={18} 
            color={activeTab === 'arrival' ? '#0C2340' : '#999'}
            style={{ transform: [{ rotate: '180deg' }] }}
          />
          <Text style={[styles.tabText, activeTab === 'arrival' && styles.activeTabText]}>
            Arrivals
          </Text>
        </TouchableOpacity>
      </View>

      {/* Flight List */}
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.flightList}>
          {currentFlights.map(renderFlightCard)}
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
  header: {
    backgroundColor: '#0C2340',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  backButton: {
    padding: 5,
  },
  placeholder: {
    width: 30,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    position: 'absolute',
    alignSelf: 'center',
    left: 0,
    right: 0,
    textAlign: 'center',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#FFD100',
  },
  tabText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#999',
  },
  activeTabText: {
    color: '#0C2340',
  },
  scrollView: {
    flex: 1,
  },
  flightList: {
    padding: 16,
  },
  flightCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  flightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  flightNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  routeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  airportInfo: {
    alignItems: 'center',
    flex: 1,
  },
  airportCode: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  time: {
    fontSize: 14,
    color: '#666',
  },
  flightPath: {
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 16,
  },
  pathLine: {
    height: 2,
    backgroundColor: '#ddd',
    width: '100%',
    marginTop: 4,
  },
  status: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4CAF50',
  },
  delayedStatus: {
    color: '#FF6B6B',
  },
  boardingStatus: {
    color: '#FFA726',
  },
  gate: {
    fontSize: 14,
    color: '#666',
  },
});