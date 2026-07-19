import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  RefreshControl,
} from "react-native";
import FontAwesome from "react-native-vector-icons/FontAwesome";
import { useFlightNotifications } from "../../hooks/useFlightNotifications";
import { useFlightRefresh } from "../../hooks/useFlightRefresh";
import { NotificationCenter } from "../../components/NotificationCenter";
import { PushNotificationBanner } from "../../components/PushNotificationBanner";
import { FlightHeader } from "../../components/FlightHeader";
import { useEffect } from "react";
import axios from "axios";
import { PermissionsAndroid } from 'react-native';
import messaging from '@react-native-firebase/messaging';
import axiosInstance from "../../services/axiosProvider";

interface Flight {
  id: string;
  flightNumber: string;
  airline: string;
  from: string;
  to: string;
  scheduledTime: string;
  actualTime: string;
  status:
    | "On Time"
    | "Delayed"
    | "Landed"
    | "Arrived"
    | "Cancelled"
    | "Boarding"
    | "Gate Change";
  gate: string;
  terminal: string;
  baggage: string;
  notificationsEnabled: boolean;
}

interface ArrivalsScreenProps {
  showHeader?: boolean;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "Landed":
    case "Arrived":
      return "#4CAF50";
    case "On Time":
    case "Boarding":
      return "#2196F3";
    case "Delayed":
    case "Gate Change":
      return "#FF6B6B";
    case "Cancelled":
      return "#9E9E9E";
    default:
      return "#999";
  }
};

export default function ArrivalsScreen(_props: ArrivalsScreenProps) {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [data, setData] = useState([]);

  const {
    notifications,
    currentNotification,
    showNotificationCenter,
    setShowNotificationCenter,
    toggleNotification,
    clearAllNotifications,
    unreadCount,
    setCurrentNotification,
  } = useFlightNotifications(flights, setFlights, "arrival");

  const { refreshing, isManualRefreshing, handleRefresh } = useFlightRefresh();
  
  const getFlightDetails = async () => {
    try{
      const response = await axios.get('http://172.17.1.217:5000/flights');
      setData(response?.data)
      
      
    } catch(error){
      console.log(error)
    }
  }

  const requestPermisssion = async () =>{
    try{
      await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS)
    } catch(error) {
      console.log(error)
    }
  }

  const subscribeToFlight = async (flightId: string) => {
  try {
    const fcmToken = await messaging().getToken();
    
    const response = await axiosInstance.post('/subscribe', {
      flight_id: flightId,
      expo_token: fcmToken
    });
    
    console.log(response?.data?.message);
  } catch (error) {
    console.log('Subscription error:', error);
    throw error;
  }
};

const handleNotificationToggle = async (flightId: string) => {
  const flight = flights.find(f => f.id === flightId);
  
  if (flight && !flight.notificationsEnabled) {
    await subscribeToFlight(flightId);
  }
  
  toggleNotification(flightId);
};

  useEffect(()=>{
    getFlightDetails()
    requestPermisssion()
  },[])

  useEffect(() => {
    if (data && Array.isArray(data) && data.length > 0) {
      const formattedFlights = data.map((flight: any) => ({
        ...flight,
        notificationsEnabled: flight.notificationsEnabled || false,
      }));
      setFlights(formattedFlights);
    }
  }, [data])

  return (
    <View style={styles.containerNoHeader}>
      <FlightHeader
        title="Today's Arriving Flights"
        unreadCount={unreadCount}
        isManualRefreshing={isManualRefreshing}
        onNotificationPress={() => setShowNotificationCenter(true)}
        onRefreshPress={() => handleRefresh(false)}
      />

      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => handleRefresh(false)}
            colors={["#0C2340"]}
          />
        }
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
              <Text style={styles.infoBarText}>
                {flights.filter((f) => f.notificationsEnabled).length} tracked
              </Text>
            </View>
          </View>

          {flights.map((flight) => (
            <View key={flight.id} style={styles.flightCard}>
              <View style={styles.cardHeader}>
                <View style={styles.flightHeaderLeft}>
                  <Text style={styles.flightNumber}>{flight.flightNumber}</Text>
                  <Text style={styles.airline}>{flight.airline}</Text>
                </View>
                <TouchableOpacity
                  style={[
                    styles.bellButton,
                    flight.notificationsEnabled && styles.bellButtonActive,
                  ]}
                  onPress={() => handleNotificationToggle(flight.id)}
                >
                  <FontAwesome
                    name={flight.notificationsEnabled ? "bell" : "bell-o"}
                    size={18}
                    color={flight.notificationsEnabled ? "#0C2340" : "#999"}
                  />
                </TouchableOpacity>
              </View>

              <View style={styles.routeContainer}>
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
              </View>

              <View style={styles.timeSection}>
                <View style={styles.timeBlock}>
                  <Text style={styles.timeLabel}>Scheduled</Text>
                  <Text style={styles.timeValue}>{flight.scheduledTime}</Text>
                </View>
                <FontAwesome name="arrow-right" size={16} color="#999" />
                <View style={styles.timeBlock}>
                  <Text style={styles.timeLabel}>Actual</Text>
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
                  <FontAwesome name="sign-in" size={14} color="#666" />
                  <Text style={styles.detailText}>Gate {flight.gate}</Text>
                </View>
                <View style={styles.detailItem}>
                  <FontAwesome name="suitcase" size={14} color="#666" />
                  <Text style={styles.detailText}>{flight.baggage}</Text>
                </View>
              </View>

              {flight.notificationsEnabled && (
                <View style={styles.notificationIndicator}>
                  <FontAwesome name="bell" size={12} color="#4CAF50" />
                  <Text style={styles.notificationText}>
                    Push notifications active
                  </Text>
                  <View style={styles.notificationPulse} />
                </View>
              )}
            </View>
          ))}
        </View>
      </ScrollView>

      <NotificationCenter
        visible={showNotificationCenter}
        notifications={notifications}
        onClose={() => setShowNotificationCenter(false)}
        onClearAll={clearAllNotifications}
      />

      {currentNotification && (
        <PushNotificationBanner
          notification={currentNotification}
          onDismiss={() => setCurrentNotification(null)}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  containerNoHeader: {
    flex: 1,
    backgroundColor: "transparent",
    position: "relative",
  },
  scrollView: { flex: 1 },
  contentContainer: {
    flex: 1,
    paddingTop: 0,
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  infoBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#fff",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 16,
    gap: 16,
  },
  infoBarSection: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  infoBarDivider: {
    width: 1,
    height: 16,
    backgroundColor: "#e0e0e0",
  },
  infoBarText: {
    fontSize: 12,
    color: "#666",
    fontWeight: "600",
  },
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
  bellButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#f5f5f5",
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  bellButtonActive: {
    backgroundColor: "#FFD100",
  },
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
  notificationIndicator: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "#f0f0f0",
    position: "relative",
  },
  notificationText: {
    fontSize: 12,
    color: "#4CAF50",
    fontWeight: "600",
  },
  notificationPulse: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#4CAF50",
    marginLeft: "auto",
  },
});
