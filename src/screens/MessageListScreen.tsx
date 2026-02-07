import React from 'react';
import { FlatList, ListRenderItem, StyleSheet, Text, View } from 'react-native';

interface MessageItem {
  id: string;
  title: string;
  preview: string;
}

interface MessageListScreenProps {
  trustLevel: number;
  messages: MessageItem[];
}

function TrustMilestoneBanner({ trustLevel }: { trustLevel: number }) {
  if (trustLevel !== 2) {
    return null;
  }

  return (
    <View style={styles.banner}>
      <Text style={styles.bannerTitle}>🛡️ Warden Status Unlocked</Text>
      <Text style={styles.bannerText}>
        Consistent security confirmations detected. Deep phishing simulations enabled.
      </Text>
    </View>
  );
}

export default function MessageListScreen({ trustLevel, messages }: MessageListScreenProps) {
  const renderItem: ListRenderItem<MessageItem> = ({ item }) => (
    <View style={styles.messageCard}>
      <Text style={styles.messageTitle}>{item.title}</Text>
      <Text style={styles.messagePreview}>{item.preview}</Text>
    </View>
  );

  return (
    <FlatList
      data={messages}
      keyExtractor={(item) => item.id}
      renderItem={renderItem}
      ListHeaderComponent={<TrustMilestoneBanner trustLevel={trustLevel} />}
      contentContainerStyle={styles.listContent}
    />
  );
}

const styles = StyleSheet.create({
  listContent: {
    padding: 12,
  },
  banner: {
    backgroundColor: '#e8f5e9',
    padding: 10,
    borderRadius: 8,
    marginBottom: 12,
  },
  bannerTitle: {
    fontWeight: 'bold',
    color: '#2e7d32',
  },
  bannerText: {
    fontSize: 12,
    marginTop: 2,
  },
  messageCard: {
    borderWidth: 1,
    borderColor: '#e4e4e4',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    backgroundColor: '#fff',
  },
  messageTitle: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 4,
  },
  messagePreview: {
    color: '#666',
  },
});
