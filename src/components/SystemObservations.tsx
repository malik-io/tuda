import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

export interface Observation {
  timestamp: string;
  note: string;
  adjustment: string;
}

interface SystemObservationsProps {
  observations: Observation[];
}

const MAX_OBSERVATIONS = 50;

export default function SystemObservations({ observations }: SystemObservationsProps) {
  const cappedObservations = observations.slice(-MAX_OBSERVATIONS);

  return (
    <View style={styles.wrapper}>
      <Text style={styles.header}>SYSTEM OBSERVATIONS</Text>
      <ScrollView style={styles.log}>
        {cappedObservations.map((obs, i) => (
          <View key={`${obs.timestamp}-${i}`} style={styles.entry}>
            <Text style={styles.timestamp}>{obs.timestamp}</Text>
            <Text style={styles.note}>• {obs.note}</Text>
            <Text style={styles.adjustment}>↳ [Action]: {obs.adjustment}</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    backgroundColor: '#f4f4f4',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  header: {
    fontSize: 12,
    fontWeight: '900',
    color: '#888',
    letterSpacing: 1,
    marginBottom: 10,
  },
  log: {
    maxHeight: 200,
  },
  entry: {
    marginBottom: 12,
    borderLeftWidth: 2,
    borderColor: '#ddd',
    paddingLeft: 10,
  },
  timestamp: {
    fontSize: 10,
    color: '#aaa',
  },
  note: {
    fontSize: 13,
    color: '#333',
  },
  adjustment: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#2ecc71',
  },
});
