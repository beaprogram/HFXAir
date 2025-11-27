import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { getTimeRemaining } from '../../utils/shopHelpers';

interface CountdownTimerProps {
  expiresAt: Date;
  onExpire?: () => void;
  size?: 'small' | 'medium' | 'large';
}

export default function CountdownTimer({ expiresAt, onExpire, size = 'medium' }: CountdownTimerProps) {
  const [timeLeft, setTimeLeft] = useState(getTimeRemaining(expiresAt));

  useEffect(() => {
    const timer = setInterval(() => {
      const remaining = getTimeRemaining(expiresAt);
      setTimeLeft(remaining);
      if (remaining.total <= 0) {
        clearInterval(timer);
        onExpire?.();
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [expiresAt, onExpire]);

  const isExpiringSoon = timeLeft.total <= 2 * 60 * 60 * 1000;
  const isExpired = timeLeft.total <= 0;
  const formatNumber = (num: number): string => num.toString().padStart(2, '0');
  const fontSize = size === 'small' ? 14 : size === 'large' ? 24 : 18;
  const labelSize = size === 'small' ? 8 : size === 'large' ? 12 : 10;

  if (isExpired) {
    return (
      <View style={styles.container}>
        <Text style={[styles.expiredText, { fontSize }]}>EXPIRED</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.timeContainer}>
        <View style={[styles.timeBlock, isExpiringSoon && styles.timeBlockWarning]}>
          <Text style={[styles.timeValue, { fontSize }, isExpiringSoon && styles.timeValueWarning]}>
            {formatNumber(timeLeft.hours)}
          </Text>
          <Text style={[styles.timeLabel, { fontSize: labelSize }]}>HRS</Text>
        </View>
        <Text style={[styles.separator, { fontSize }]}>:</Text>
        <View style={[styles.timeBlock, isExpiringSoon && styles.timeBlockWarning]}>
          <Text style={[styles.timeValue, { fontSize }, isExpiringSoon && styles.timeValueWarning]}>
            {formatNumber(timeLeft.minutes)}
          </Text>
          <Text style={[styles.timeLabel, { fontSize: labelSize }]}>MIN</Text>
        </View>
        <Text style={[styles.separator, { fontSize }]}>:</Text>
        <View style={[styles.timeBlock, isExpiringSoon && styles.timeBlockWarning]}>
          <Text style={[styles.timeValue, { fontSize }, isExpiringSoon && styles.timeValueWarning]}>
            {formatNumber(timeLeft.seconds)}
          </Text>
          <Text style={[styles.timeLabel, { fontSize: labelSize }]}>SEC</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center' },
  timeContainer: { flexDirection: 'row', alignItems: 'center' },
  timeBlock: { alignItems: 'center', backgroundColor: '#f0f0f0', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, minWidth: 40 },
  timeBlockWarning: { backgroundColor: '#FFF3E0' },
  timeValue: { fontWeight: 'bold', color: '#0C2340', fontVariant: ['tabular-nums'] },
  timeValueWarning: { color: '#E65100' },
  timeLabel: { color: '#666', marginTop: 2 },
  separator: { fontWeight: 'bold', color: '#0C2340', marginHorizontal: 4 },
  expiredText: { fontWeight: 'bold', color: '#F44336' },
});