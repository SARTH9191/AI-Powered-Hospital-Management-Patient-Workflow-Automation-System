# PostgreSQL Migration - Dual Database Strategy
# ZERO RISK: Writes to both JSON and PostgreSQL, JSON stays as backup

## Phase 1: PostgreSQL Setup (30 min)

### Step 1: Install PostgreSQL Python Driver
```bash
pip install psycopg2-binary sqlalchemy alembic
```

### Step 2: Install PostgreSQL Server (if not installed)
- Download: https://www.postgresql.org/download/windows/
- Version: PostgreSQL 15 or 16
- Default port: 5432
- Create database: `hospital_ai_agent`

### Step 3: Create Database
```sql
-- Connect to PostgreSQL using pgAdmin or psql
CREATE DATABASE hospital_ai_agent;
CREATE USER hospital_admin WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE hospital_ai_agent TO hospital_admin;
```

### Step 4: Environment Configuration
Add to `.env`:
```
# PostgreSQL Configuration
DATABASE_URL=postgresql://hospital_admin:secure_password_123@localhost:5432/hospital_ai_agent
DATABASE_TYPE=dual  # Options: json, postgresql, dual

# Database Fallback Settings
USE_JSON_FALLBACK=true
JSON_PRIMARY=true  # During migration, JSON is primary source
SYNC_INTERVAL_SECONDS=60  # How often to sync JSON → PostgreSQL
```

## Phase 2: Database Schema Creation (15 min)

We'll create tables for:
1. workflow_states (patient workflow state)
2. patients (patient records)
3. appointments (scheduling)
4. lab_tests (lab orders & results)
5. billing (invoices & payments)
6. medical_records (medical history)
7. audit_log (all database operations)

## Phase 3: Dual-Write Implementation (30 min)

### Strategy:
1. Write to JSON (primary, existing)
2. Async write to PostgreSQL (secondary)
3. If PostgreSQL fails → log error, continue with JSON
4. Read from JSON (until PostgreSQL is proven stable)
5. Background sync job: JSON → PostgreSQL every 60 seconds

### Benefits:
- ✅ **ZERO RISK**: JSON always works, PostgreSQL is optional
- ✅ **Zero downtime**: System continues if PostgreSQL fails
- ✅ **Gradual migration**: Move to PostgreSQL when confident
- ✅ **Easy rollback**: Just disable PostgreSQL, use JSON
- ✅ **Data validation**: Compare JSON vs PostgreSQL data

## Phase 4: Monitoring & Validation (15 min)

### Metrics to track:
- PostgreSQL write success rate
- JSON vs PostgreSQL sync accuracy
- Query performance comparison
- Error rates
- Sync lag time

### Dashboard:
- Real-time sync status
- Data consistency checks
- Performance graphs
- Error alerts

---

## Implementation Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Install dependencies | 5 min | ⏳ Next |
| 2 | Create database schema | 15 min | ⏳ |
| 3 | Implement dual-write | 30 min | ⏳ |
| 4 | Testing & validation | 15 min | ⏳ |
| 5 | Monitoring setup | 10 min | ⏳ |
| 6 | Documentation | 5 min | ⏳ |
| **TOTAL** | | **1.5 hours** | |

---

## Risk Mitigation

### If PostgreSQL fails:
1. System continues with JSON (no interruption)
2. Error logged to file
3. Admin notified
4. Retry queue activated
5. JSON remains source of truth

### Rollback Plan:
```python
# In .env, simply change:
DATABASE_TYPE=json  # Disables PostgreSQL completely
```

System continues working with JSON only.

---

## Success Criteria

✅ All JSON writes succeed (existing behavior)
✅ PostgreSQL writes succeed 95%+ of the time
✅ Data consistency 99%+ between JSON and PostgreSQL
✅ Performance: PostgreSQL writes < 100ms
✅ Zero user-facing errors
✅ Easy rollback capability

---

**Ready to start? Let's begin with Phase 1!**
