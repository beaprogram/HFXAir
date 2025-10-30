import FontAwesome from '@expo/vector-icons/FontAwesome';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

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
    hasNotification: true,
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
    hasNotification: true,
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
    hasNotification: false,
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
    hasNotification: true,
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
    hasNotification: false,
  },
];

export default function TabOneScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Flight Status</Text>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {mockFlights.map((flight) => (
          <TouchableOpacity key={flight.id} style={styles.flightCard}>
            <View style={styles.flightHeader}>
              <Text style={styles.flightNumber}>{flight.flightNumber}</Text>
              {flight.hasNotification && (
                <FontAwesome name="bell" size={20} color="#FF6B6B" />
              )}
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
            
            <View style={styles.flightFooter}>
              <View style={styles.statusContainer}>
                <Text style={[
                  styles.status,
                  flight.status === 'Delayed' && styles.delayedStatus,
                  flight.status === 'Boarding' && styles.boardingStatus
                ]}>
                  {flight.status}
                </Text>
                <Text style={styles.gate}>Gate: {flight.gate}</Text>
              </View>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 20,
    color: '#333',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 16,
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
  flightFooter: {
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 12,
  },
  statusContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
