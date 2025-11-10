import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Modal,
} from "react-native";
import FontAwesome from "react-native-vector-icons/FontAwesome";

interface Notification {
  id: string;
  flightNumber: string;
  type: "gate_change" | "status_update" | "delay" | "boarding";
  message: string;
  timestamp: Date;
  read: boolean;
}

interface NotificationCenterProps {
  visible: boolean;
  notifications: Notification[];
  onClose: () => void;
  onClearAll: () => void;
}

export const NotificationCenter = ({
  visible,
  notifications,
  onClose,
  onClearAll,
}: NotificationCenterProps) => {
  if (!visible) return null;

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
      presentationStyle="overFullScreen"
      statusBarTranslucent={true}
    >
      <TouchableOpacity
        style={styles.modalOverlay}
        activeOpacity={1}
        onPress={onClose}
      >
        <TouchableOpacity
          activeOpacity={1}
          style={styles.modalContent}
          onPress={(e) => e.stopPropagation()}
        >
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Notification Center</Text>
            <View style={styles.modalHeaderActions}>
              {notifications.length > 0 && (
                <TouchableOpacity
                  onPress={onClearAll}
                  style={styles.clearAllButton}
                >
                  <Text style={styles.clearAllText}>Clear All</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity onPress={onClose}>
                <FontAwesome name="times" size={24} color="#0C2340" />
              </TouchableOpacity>
            </View>
          </View>
          <ScrollView
            style={styles.notificationList}
            contentContainerStyle={styles.notificationListContent}
          >
            {notifications.length === 0 ? (
              <View style={styles.emptyNotifications}>
                <FontAwesome name="bell-slash-o" size={48} color="#ccc" />
                <Text style={styles.emptyNotificationsText}>
                  No notifications yet
                </Text>
                <Text style={styles.emptyNotificationsSubtext}>
                  Enable notifications for flights to receive real-time updates
                </Text>
              </View>
            ) : (
              notifications.map((notif) => (
                <View key={notif.id} style={styles.notificationItem}>
                  <View style={styles.notificationItemHeader}>
                    <Text style={styles.notificationItemFlight}>
                      Flight {notif.flightNumber}
                    </Text>
                    <Text style={styles.notificationItemTime}>
                      {notif.timestamp.toLocaleTimeString("en-US", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </Text>
                  </View>
                  <Text style={styles.notificationItemMessage}>
                    {notif.message}
                  </Text>
                </View>
              ))
            )}
          </ScrollView>
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    height: "85%",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 20,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
    backgroundColor: "#fff",
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#0C2340",
  },
  modalHeaderActions: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
  },
  clearAllButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: "#FFD100",
    borderRadius: 16,
  },
  clearAllText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#0C2340",
  },
  notificationList: {
    flex: 1,
  },
  notificationListContent: {
    paddingBottom: 20,
  },
  emptyNotifications: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 60,
    paddingHorizontal: 40,
  },
  emptyNotificationsText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#999",
    marginTop: 16,
  },
  emptyNotificationsSubtext: {
    fontSize: 13,
    color: "#bbb",
    textAlign: "center",
    marginTop: 8,
    lineHeight: 20,
  },
  notificationItem: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  notificationItemHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  notificationItemFlight: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#0C2340",
  },
  notificationItemTime: {
    fontSize: 11,
    color: "#999",
  },
  notificationItemMessage: {
    fontSize: 13,
    color: "#666",
    lineHeight: 20,
  },
});