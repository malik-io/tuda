import React, { useState } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import Slider from '@react-native-community/slider';

interface ToneProfile {
  directness: number;
  technicality: number;
  conciseness: number;
}

export interface PersonaSeed {
  tone_profile: ToneProfile;
  language_style: 'technical' | 'neutral';
  trust_level: number;
}

interface OnboardingScreenProps {
  onComplete: (personaSeed: PersonaSeed) => void;
}

export default function OnboardingScreen({ onComplete }: OnboardingScreenProps) {
  const [prefs, setPrefs] = useState<ToneProfile>({
    directness: 0.5,
    technicality: 0.5,
    conciseness: 0.8,
  });

  const handleFinish = () => {
    const personaSeed: PersonaSeed = {
      tone_profile: { ...prefs },
      language_style: prefs.technicality > 0.7 ? 'technical' : 'neutral',
      trust_level: 0,
    };

    onComplete(personaSeed);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Initialize TUDA Persona</Text>
      <Text style={styles.subtitle}>How should the agent observe your data?</Text>

      <View style={styles.controlGroup}>
        <Text>Tone: {prefs.directness > 0.5 ? 'Direct' : 'Gentle'}</Text>
        <Slider
          value={prefs.directness}
          minimumValue={0}
          maximumValue={1}
          step={0.01}
          onValueChange={(v) => setPrefs({ ...prefs, directness: v })}
        />
      </View>

      <View style={styles.controlGroup}>
        <Text>
          Complexity: {prefs.technicality > 0.5 ? 'Detailed' : 'Plain English'}
        </Text>
        <Slider
          value={prefs.technicality}
          minimumValue={0}
          maximumValue={1}
          step={0.01}
          onValueChange={(v) => setPrefs({ ...prefs, technicality: v })}
        />
      </View>

      <View style={styles.controlGroup}>
        <Text>Conciseness: {Math.round(prefs.conciseness * 100)}%</Text>
        <Slider
          value={prefs.conciseness}
          minimumValue={0}
          maximumValue={1}
          step={0.01}
          onValueChange={(v) => setPrefs({ ...prefs, conciseness: v })}
        />
      </View>

      <Button title="Initialize Consciousness" onPress={handleFinish} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 40,
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    color: '#666',
    marginBottom: 30,
  },
  controlGroup: {
    marginBottom: 25,
  },
});
