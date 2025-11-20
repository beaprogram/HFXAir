import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';

interface FlightCardProps {
  flight: {
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
  };
  type: 'arrival' | 'departure';
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "Landed":
    case "Arrived":
    case "On Time":
    case "Check-In":
      return "#4CAF50";
    case "Boarding":
      return "#FFA726";
    case "Delayed":
    case "Gate Change":
      return "#FF6B6B";
    case "Departed":
      return "#2196F3";
    case "Cancelled":
      return "#9E9E9E";
    default:
      return "#999";
  }
};

export const FlightCard: React.FC<FlightCardProps> = ({ flight, type }) => {
  return (
    <View style={styles.flightCard}>
      <View style={styles.cardHeader}>
        <View style={styles.flightHeaderLeft}>
          <Text style={styles.flightNumber}>{flight.flightNumber}</Text>
          <Text style={styles.airline}>{flight.airline}</Text>
        </View>
      </View>

      <View style={styles.routeContainer}>
        {type === 'arrival' ? (
          <>
            <View style={styles.routeInfo}>
              <FontAwesome
                name="plane"
                size={14}
                color="#0C2340"
                style={{ transform: [{ rotate: "45deg" }] }}
              />
              <Text style={styles.routeLabel}>From:</Text>
              <Text style={styles.fromCity}>{flight.from}</Text>
            </View>
            <View style={styles.routeInfo}>
              <FontAwesome name="map-marker" size={14} color="#0C2340" />
              <Text style={styles.routeLabel}>To:</Text>
              <Text style={styles.toCity}>{flight.to}</Text>
            </View>
          </>
        ) : (
          <View style={styles.routeInfo}>
            <FontAwesome name="plane" size={14} color="#0C2340" />
            <Text style={styles.routeLabel}>Destination:</Text>
            <Text style={styles.toCity}>{flight.to}</Text>
          </View>
        )}
      </View>

      <View style={styles.timeSection}>
        <View style={styles.timeBlock}>
          <Text style={styles.timeLabel}>Scheduled</Text>
          <Text style={styles.timeValue}>{flight.scheduledTime}</Text>
        </View>
        <FontAwesome name="arrow-right" size={16} color="#999" />
        <View style={styles.timeBlock}>
          <Text style={styles.timeLabel}>
            {type === 'arrival' ? 'Actual' : 'Departure'}
          </Text>
          <Text
            style={[
              styles.timeValue,
              flight.status === "Delayed" && styles.delayedTime,
            ]}
          >
            {flight?.actualTime || "-"}
          </Text>
        </View>
      </View>

      <View style={styles.statusSection}>
        <View
          style={[
            styles.statusBadge,
            { backgroundColor: getStatusColor(flight.status) },
          ]}
        >
          <Text style={styles.statusText}>{flight.status}</Text>
        </View>
      </View>

      <View style={styles.detailsSection}>
        <View style={styles.detailItem}>
          <FontAwesome name="building" size={14} color="#666" />
          <Text style={styles.detailText}>{flight.terminal}</Text>
        </View>
        <View style={styles.detailItem}>
          <FontAwesome 
            name={type === 'arrival' ? "sign-in" : "sign-out"} 
            size={14} 
            color="#666" 
          />
          <Text style={styles.detailText}>Gate {flight.gate}</Text>
        </View>
        {type === 'arrival' && flight.baggage && (
          <View style={styles.detailItem}>
            <FontAwesome name="suitcase" size={14} color="#666" />
            <Text style={styles.detailText}>{flight.baggage}</Text>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  flightCard: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 16,
  },
  flightHeaderLeft: { flex: 1 },
  flightNumber: { fontSize: 22, fontWeight: "bold", color: "#0C2340" },
  airline: { fontSize: 14, color: "#666", marginTop: 4 },
  routeContainer: {
    backgroundColor: "#f9f9f9",
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    gap: 8,
  },
  routeInfo: { flexDirection: "row", alignItems: "center", gap: 8 },
  routeLabel: {
    fontSize: 11,
    color: "#999",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    fontWeight: "600",
  },
  fromCity: { fontSize: 15, fontWeight: "600", color: "#333" },
  toCity: { fontSize: 15, fontWeight: "bold", color: "#0C2340" },
  timeSection: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    paddingVertical: 16,
    backgroundColor: "#f9f9f9",
    borderRadius: 12,
    marginBottom: 16,
  },
  timeBlock: { alignItems: "center" },
  timeLabel: { fontSize: 12, color: "#999", marginBottom: 4 },
  timeValue: { fontSize: 24, fontWeight: "bold", color: "#0C2340" },
  delayedTime: { color: "#FF6B6B" },
  statusSection: { alignItems: "center", marginBottom: 16 },
  statusBadge: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20 },
  statusText: { color: "#fff", fontSize: 14, fontWeight: "600" },
  detailsSection: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: "#f0f0f0",
  },
  detailItem: { flexDirection: "row", alignItems: "center", gap: 6 },
  detailText: { fontSize: 13, color: "#666" },
});
