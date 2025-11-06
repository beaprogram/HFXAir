import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';

interface Flight {
  id: string;
  flightNumber: string;
  airline: string;
  from: string;
  to: string;
  scheduledTime: string;
  actualTime: string;
  status: 'On Time' | 'Delayed' | 'Landed' | 'Arrived' | 'Cancelled' | 'Boarding' | 'Gate Change';
  gate: string;
  terminal: string;
  baggage: string;
}

interface ArrivalsScreenProps {
  showHeader?: boolean;
}

const generateMockFlights = (): Flight[] => [
  {
    id: '1',
    flightNumber: 'AA1234',
    airline: 'American Airlines',
    from: 'New York (JFK)',
    to: 'Halifax (YHZ)',
    scheduledTime: '11:45',
    actualTime: '11:42',
    status: 'On Time',
    gate: 'A12',
    terminal: 'Terminal 1',
    baggage: 'Carousel 3',
  },
  {
    id: '2',
    flightNumber: 'AC5678',
    airline: 'Air Canada',
    from: 'Toronto (YYZ)',
    to: 'Halifax (YHZ)',
    scheduledTime: '16:35',
    actualTime: '17:10',
    status: 'Delayed',
    gate: 'B8',
    terminal: 'Terminal 1',
    baggage: 'Carousel 1',
  },
  {
    id: '3',
    flightNumber: 'WS9012',
    airline: 'WestJet',
    from: 'Calgary (YYC)',
    to: 'Halifax (YHZ)',
    scheduledTime: '17:15',
    actualTime: '17:15',
    status: 'On Time',
    gate: 'C15',
    terminal: 'Terminal 1',
    baggage: 'Carousel 2',
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Landed':
    case 'Arrived':
      return '#4CAF50';
    case 'On Time':
    case 'Boarding':
      return '#2196F3';
    case 'Delayed':
    case 'Gate Change':
      return '#FF6B6B';
    case 'Cancelled':
      return '#9E9E9E';
    default:
      return '#999';
  }
};

export default function ArrivalsScreen({ showHeader = true }: ArrivalsScreenProps) {
  const [flights] = useState<Flight[]>(generateMockFlights());

  return (
    <View style={styles.containerNoHeader}>
      <View style={styles.embeddedHeader}>
        <Text style={styles.subtitle}>Today's Arriving Flights</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity style={styles.notificationButtonEmbedded}>
            <FontAwesome name="bell" size={18} color="#0C2340" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.refreshButtonEmbedded}>
            <FontAwesome name="refresh" size={18} color="#0C2340" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView 
        style={styles.scrollView} 
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.contentContainer}>
          <View style={styles.infoBar}>
            <View style={styles.infoBarSection}>
              <FontAwesome name="clock-o" size={14} color="#666" />
              <Text style={styles.infoBarText}>Auto-refresh: 30s</Text>
            </View>
            <View style={styles.infoBarDivider} />
            <View style={styles.infoBarSection}>
              <FontAwesome name="bell" size={14} color="#666" />
              <Text style={styles.infoBarText}>0 tracked</Text>
            </View>
          </View>

          {flights.map((flight) => (
            <View key={flight.id} style={styles.flightCard}>
              <View style={styles.cardHeader}>
                <View style={styles.flightHeaderLeft}>
                  <Text style={styles.flightNumber}>{flight.flightNumber}</Text>
                  <Text style={styles.airline}>{flight.airline}</Text>
                </View>
                <TouchableOpacity style={styles.bellButton}>
                  <FontAwesome name="bell-o" size={18} color="#999" />
                </TouchableOpacity>
              </View>

              <View style={styles.routeContainer}>
                <View style={styles.routeInfo}>
                  <FontAwesome name="plane" size={14} color="#0C2340" style={{ transform: [{ rotate: '45deg' }] }} />
                  <Text style={styles.routeLabel}>From:</Text>
                  <Text style={styles.fromCity}>{flight.from}</Text>
                </View>
                <View style={styles.routeInfo}>
                  <FontAwesome name="map-marker" size={14} color="#0C2340" />
                  <Text style={styles.routeLabel}>To:</Text>
                  <Text style={styles.toCity}>{flight.to}</Text>
                </View>
              </View>

              <View style={styles.timeSection}>
                <View style={styles.timeBlock}>
                  <Text style={styles.timeLabel}>Scheduled</Text>
                  <Text style={styles.timeValue}>{flight.scheduledTime}</Text>
                </View>
                <FontAwesome name="arrow-right" size={16} color="#999" />
                <View style={styles.timeBlock}>
                  <Text style={styles.timeLabel}>Actual</Text>
                  <Text style={[styles.timeValue, flight.status === 'Delayed' && styles.delayedTime]}>
                    {flight.actualTime}
                  </Text>
                </View>
              </View>

              <View style={styles.statusSection}>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(flight.status) }]}>
                  <Text style={styles.statusText}>{flight.status}</Text>
                </View>
              </View>

              <View style={styles.detailsSection}>
                <View style={styles.detailItem}>
                  <FontAwesome name="building" size={14} color="#666" />
                  <Text style={styles.detailText}>{flight.terminal}</Text>
                </View>
                <View style={styles.detailItem}>
                  <FontAwesome name="sign-in" size={14} color="#666" />
                  <Text style={styles.detailText}>Gate {flight.gate}</Text>
                </View>
                <View style={styles.detailItem}>
                  <FontAwesome name="suitcase" size={14} color="#666" />
                  <Text style={styles.detailText}>{flight.baggage}</Text>
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
  containerNoHeader: { flex: 1, backgroundColor: 'transparent', position: 'relative' },
  embeddedHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  subtitle: { fontSize: 18, fontWeight: '600', color: '#0C2340' },
  headerButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  notificationButtonEmbedded: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    position: 'relative',
  },
  refreshButtonEmbedded: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  scrollView: { flex: 1 },
  contentContainer: { flex: 1, paddingTop: 0, paddingHorizontal: 16, paddingBottom: 20 },
  infoBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 16,
    gap: 16,
  },
  infoBarSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  infoBarDivider: {
    width: 1,
    height: 16,
    backgroundColor: '#e0e0e0',
  },
  infoBarText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  flightCard: { 
    backgroundColor: '#fff', 
    borderRadius: 16, 
    padding: 20, 
    marginBottom: 16, 
    shadowColor: '#000', 
    shadowOffset: { width: 0, height: 2 }, 
    shadowOpacity: 0.1, 
    shadowRadius: 4, 
    elevation: 3 
  },
  cardHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'flex-start', 
    marginBottom: 16 
  },
  flightHeaderLeft: { flex: 1 },
  flightNumber: { fontSize: 22, fontWeight: 'bold', color: '#0C2340' },
  airline: { fontSize: 14, color: '#666', marginTop: 4 },
  bellButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  routeContainer: {
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    gap: 8,
  },
  routeInfo: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  routeLabel: { 
    fontSize: 11, 
    color: '#999', 
    textTransform: 'uppercase', 
    letterSpacing: 0.5,
    fontWeight: '600',
  },
  fromCity: { fontSize: 15, fontWeight: '600', color: '#333' },
  toCity: { fontSize: 15, fontWeight: 'bold', color: '#0C2340' },
  timeSection: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-around', 
    paddingVertical: 16, 
    backgroundColor: '#f9f9f9', 
    borderRadius: 12, 
    marginBottom: 16 
  },
  timeBlock: { alignItems: 'center' },
  timeLabel: { fontSize: 12, color: '#999', marginBottom: 4 },
  timeValue: { fontSize: 24, fontWeight: 'bold', color: '#0C2340' },
  delayedTime: { color: '#FF6B6B' },
  statusSection: { alignItems: 'center', marginBottom: 16 },
  statusBadge: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20 },
  statusText: { color: '#fff', fontSize: 14, fontWeight: '600' },
  detailsSection: { 
    flexDirection: 'row', 
    justifyContent: 'space-around', 
    paddingTop: 16, 
    borderTopWidth: 1, 
    borderTopColor: '#f0f0f0' 
  },
  detailItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  detailText: { fontSize: 13, color: '#666' },
});