export interface ActorBlock {
  actor_id: string;
  actor_name: string;
  persona: string | null;
  actor_type: 'human' | 'demo' | 'agent' | 'system';
}

export interface DomainEvent {
  event_id: string;
  event_type: string;
  topic: string;
  occurred_at: string;
  actor: ActorBlock;
  source: string;
  entity_type: string;
  entity_id: string;
  correlation_id: string | null;
  payload: Record<string, unknown>;
  summary: string;
}

export interface EventFilter {
  topic?: string;
  event_type?: string;
  entity_id?: string;
  actor_id?: string;
  source?: string;
  correlation_id?: string;
}
