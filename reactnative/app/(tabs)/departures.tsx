import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';

interface Flight {
  id: string;
  flightNumber: string;
  airline: string;
  to: string;
  scheduledTime: string;
  actualTime: string;
  status: 'On Time' | 'Delayed' | 'Boarding' | 'Check-In' | 'Departed' | 'Cancelled' | 'Gate Change';
  gate: string;
  terminal: string;
  boardingTime: string;
}

interface DeparturesScreenProps {
  showHeader?: boolean;
}

const generateMockFlights = (): Flight[] => [
  {
    id: '1',
    flightNumber: 'AC1001',
    airline: 'Air Canada',
    to: 'Montreal (YUL)',
    scheduledTime: '08:30',
    actualTime: '08:30',
    status: 'On Time',
    gate: 'A15',
    terminal: 'Terminal 1',
    boardingTime: '08:00',
  },
  {
    id: '2',
    flightNumber: 'WS2345',
    airline: 'WestJet',
    to: 'Vancouver (YVR)',
    scheduledTime: '10:15',
    actualTime: '10:15',
    status: 'Boarding',
    gate: 'B22',
    terminal: 'Terminal 1',
    boardingTime: '09:45',
  },
  {
    id: '3',
    flightNumber: 'AA4567',
    airline: 'American Airlines',
    to: 'New York (JFK)',
    scheduledTime: '12:45',
    actualTime: '13:20',
    status: 'Delayed',
    gate: 'C8',
    terminal: 'Terminal 1',
    boardingTime: '12:50',
  },
  {
    id: '4',
    flightNumber: 'UA7890',
    airline: 'United Airlines',
    to: 'Chicago (ORD)',
    scheduledTime: '14:30',
    actualTime: '14:30',
    status: 'On Time',
    gate: 'A10',
    terminal: 'Terminal 1',
    boardingTime: '14:00',
  },
  {
    id: '5',
    flightNumber: 'DL3210',
    airline: 'Delta Airlines',
    to: 'Atlanta (ATL)',
    scheduledTime: '16:00',
    actualTime: '16:00',
    status: 'Check-In',
    gate: 'B5',
    terminal: 'Terminal 1',
    boardingTime: '15:30',
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Boarding':
      return '#FFA726';
    case 'On Time':
    case 'Check-In':
      return '#4CAF50';
    case 'Delayed':
    case 'Gate Change':
      return '#FF6B6B';
    case 'Departed':
      return '#2196F3';
    case 'Cancelled':
      return '#9E9E9E';
    default:
      return '#999';
  }
};

export default function DeparturesScreen({ showHeader = true }: DeparturesScreenProps) {
  const [flights] = useState<Flight[]>(generateMockFlights());

  return (
    <View style={styles.containerNoHeader}>
      <View style={styles.embeddedHeader}>
        <Text style={styles.subtitle}>Today's Departing Flights</Text>
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
                  <FontAwesome name="plane" size={14} color="#0C2340" />
                  <Text style={styles.routeLabel}>Destination:</Text>
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
                  <Text style={styles.timeLabel}>Departure</Text>
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
                  <FontAwesome name="sign-out" size={14} color="#666" />
                  <Text style={styles.detailText}>Gate {flight.gate}</Text>
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
  },
  routeInfo: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  routeLabel: { 
    fontSize: 11, 
    color: '#999', 
    textTransform: 'uppercase', 
    letterSpacing: 0.5,
    fontWeight: '600',
  },
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