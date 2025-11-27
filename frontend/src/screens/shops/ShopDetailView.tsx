import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Shop } from '../../types/shops';
import { getShopStatusText, formatTime, getCurrentDay } from '../../utils/shopHelpers';
import StatusBadge from '../../components/shops/StatusBadge';

interface ShopDetailViewProps {
  shop: Shop;
  onBack: () => void;
  onViewCatalog: () => void;
}

export default function ShopDetailView({ shop, onBack, onViewCatalog }: ShopDetailViewProps) {
  const status = getShopStatusText(shop);
  const today = getCurrentDay();

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <FontAwesome name="arrow-left" size={20} color="#0C2340" />
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>{shop.name}</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.statusCard}>
          <View style={styles.statusHeader}>
            <StatusBadge status={status.isOpen ? 'Open' : 'Closed'} />
            <Text style={[styles.statusText, { color: status.isOpen ? '#2E7D32' : '#C62828' }]}>{status.text}</Text>
          </View>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.sectionTitle}>About</Text>
          <Text style={styles.description}>{shop.description}</Text>
          <View style={styles.infoRow}>
            <FontAwesome name="map-marker" size={16} color="#666" />
            <Text style={styles.infoText}>{shop.location}</Text>
          </View>
          <View style={styles.infoRow}>
            <FontAwesome name="building" size={16} color="#666" />
            <Text style={styles.infoText}>{shop.terminal}</Text>
          </View>
          {shop.gate && (
            <View style={styles.infoRow}>
              <FontAwesome name="plane" size={16} color="#666" />
              <Text style={styles.infoText}>{shop.gate}</Text>
            </View>
          )}
        </View>

        {shop.weeklyHours && shop.weeklyHours.length > 0 && (
          <View style={styles.hoursCard}>
            <Text style={styles.sectionTitle}>Weekly Hours</Text>
            {shop.weeklyHours.map((hours, index) => (
              <View key={index} style={[styles.hoursRow, hours.day === today && styles.hoursRowToday]}>
                <Text style={[styles.dayText, hours.day === today && styles.dayTextToday]}>
                  {hours.day}{hours.day === today && ' (Today)'}
                </Text>
                <Text style={[styles.hoursText, hours.isClosed && styles.closedText]}>
                  {hours.isClosed ? 'Closed' : `${formatTime(hours.openTime)} - ${formatTime(hours.closeTime)}`}
                </Text>
              </View>
            ))}
          </View>
        )}

        {shop.exceptionHours && shop.exceptionHours.length > 0 && (
          <View style={styles.exceptionsCard}>
            <Text style={styles.sectionTitle}>Holiday/Exception Hours</Text>
            {shop.exceptionHours.map((exception, index) => (
              <View key={index} style={styles.exceptionRow}>
                <View style={styles.exceptionHeader}>
                  <Text style={styles.exceptionDate}>{exception.date}</Text>
                  <Text style={styles.exceptionReason}>{exception.description}</Text>
                </View>
                <Text style={[styles.exceptionHours, exception.isClosed && styles.closedText]}>
                  {exception.isClosed ? 'Closed' : `${formatTime(exception.openTime)} - ${formatTime(exception.closeTime)}`}
                </Text>
              </View>
            ))}
          </View>
        )}

        <View style={styles.bottomPadding} />
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity style={styles.catalogButton} onPress={onViewCatalog}>
          <FontAwesome name="shopping-bag" size={18} color="#0C2340" />
          <Text style={styles.catalogButtonText}>View Catalog</Text>
          <FontAwesome name="chevron-right" size={14} color="#0C2340" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  backButton: { padding: 8 },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#0C2340', flex: 1, textAlign: 'center', marginHorizontal: 8 },
  placeholder: { width: 36 },
  content: { flex: 1, padding: 16 },
  statusCard: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12 },
  statusHeader: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  statusText: { fontSize: 14, fontWeight: '500' },
  infoCard: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#0C2340', marginBottom: 12 },
  description: { fontSize: 14, color: '#666', lineHeight: 20, marginBottom: 16 },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 8 },
  infoText: { fontSize: 14, color: '#333' },
  hoursCard: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12 },
  hoursRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#f0f0f0' },
  hoursRowToday: { backgroundColor: '#FFF8E1', marginHorizontal: -16, paddingHorizontal: 16, borderRadius: 8 },
  dayText: { fontSize: 14, color: '#333' },
  dayTextToday: { fontWeight: 'bold', color: '#0C2340' },
  hoursText: { fontSize: 14, color: '#666' },
  closedText: { color: '#C62828' },
  exceptionsCard: { backgroundColor: '#FFF3E0', borderRadius: 12, padding: 16, marginBottom: 12 },
  exceptionRow: { marginBottom: 12, paddingBottom: 12, borderBottomWidth: 1, borderBottomColor: '#FFE0B2' },
  exceptionHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  exceptionDate: { fontSize: 14, fontWeight: '600', color: '#E65100' },
  exceptionReason: { fontSize: 12, color: '#666' },
  exceptionHours: { fontSize: 14, color: '#333' },
  bottomPadding: { height: 20 },
  footer: { padding: 16, backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#e0e0e0' },
  catalogButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#FFD100', paddingVertical: 14, borderRadius: 12, gap: 10 },
  catalogButtonText: { fontSize: 16, fontWeight: 'bold', color: '#0C2340' },
});