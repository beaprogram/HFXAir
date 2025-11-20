import React, { useState, useEffect } from 'react';
import { ScrollView, StyleSheet, Text, View, TouchableOpacity, StatusBar, RefreshControl } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import axios from 'axios';
import { FlightCard } from "../../components/FlightCard";

interface Flight {
  id: string;
  flightNumber: string;
  airline: string;
  from: string;
  to: string;
  scheduledTime: string;
  actualTime?: string;
  status: string;
  gate: string;
  terminal: string;
  baggage?: string;
  boardingTime?: string;
}

interface GuestFlightsScreenProps {
  onBack: () => void;
}

export default function GuestFlightsScreen({ onBack }: GuestFlightsScreenProps) {
  const [activeTab, setActiveTab] = useState<'departure' | 'arrival'>('departure');
  const [allFlights, setAllFlights] = useState<Flight[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch flights from backend
  const getFlightDetails = async () => {
    try {
      const response = await axios.get('http://172.17.1.217:5000/flights');
      if (response?.data && Array.isArray(response.data)) {
        setAllFlights(response.data);
      }
    } catch (error) {
      console.log('Error fetching flights:', error);
    }
  };

  // Initial fetch
  useEffect(() => {
    getFlightDetails();
  }, []);

  // Handle pull-to-refresh
  const onRefresh = async () => {
    setRefreshing(true);
    await getFlightDetails();
    setRefreshing(false);
  };

  // Filter flights based on active tab
  const arrivals = allFlights.filter(
    (flight) => flight.from !== "Halifax (YHZ)"
  );
  
  const departures = allFlights.filter(
    (flight) => flight.from === "Halifax (YHZ)"
  );

  const currentFlights = activeTab === 'departure' ? departures : arrivals;

  const handleBack = () => {
    onBack();
  };

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
      <ScrollView 
        style={styles.scrollView} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={["#0C2340"]}
          />
        }
      >
        <View style={styles.flightList}>
          {currentFlights.length > 0 ? (
            currentFlights.map((flight) => (
              <FlightCard 
                key={flight.id} 
                flight={flight} 
                type={activeTab}
              />
            ))
          ) : (
            <View style={styles.emptyState}>
              <FontAwesome name="plane" size={48} color="#ccc" />
              <Text style={styles.emptyText}>No flights available</Text>
            </View>
          )}
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
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginTop: 16,
  },
});