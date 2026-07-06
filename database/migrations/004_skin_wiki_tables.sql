-- Migration: Skin-Wiki Content Management Tables
-- Requirements: 10.5, 16.6
-- Description: Creates tables for educational content management with version tracking

-- ============================================================================
-- Skin-Wiki Articles Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS skin_wiki_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    cancer_type TEXT,
    slug TEXT UNIQUE,
    summary TEXT,
    image_url TEXT,
    tags TEXT[],
    version INTEGER DEFAULT 1,
    published BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_skin_wiki_articles_cancer_type ON skin_wiki_articles(cancer_type);
CREATE INDEX idx_skin_wiki_articles_published ON skin_wiki_articles(published);
CREATE INDEX idx_skin_wiki_articles_slug ON skin_wiki_articles(slug);
CREATE INDEX idx_skin_wiki_articles_created_at ON skin_wiki_articles(created_at DESC);

-- ============================================================================
-- Skin-Wiki Version History Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS skin_wiki_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES skin_wiki_articles(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content JSONB NOT NULL,
    updated_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, version)
);

-- Indexes for version history
CREATE INDEX idx_skin_wiki_versions_article ON skin_wiki_versions(article_id);
CREATE INDEX idx_skin_wiki_versions_version ON skin_wiki_versions(article_id, version DESC);

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS
ALTER TABLE skin_wiki_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE skin_wiki_versions ENABLE ROW LEVEL SECURITY;

-- Public read access for published articles
CREATE POLICY "Public can view published articles"
    ON skin_wiki_articles
    FOR SELECT
    USING (published = true);

-- Admins can do everything
CREATE POLICY "Admins can manage articles"
    ON skin_wiki_articles
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Admins can view version history"
    ON skin_wiki_versions
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

-- ============================================================================
-- Triggers for automatic timestamp updates
-- ============================================================================

CREATE OR REPLACE FUNCTION update_skin_wiki_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_skin_wiki_articles_updated_at
    BEFORE UPDATE ON skin_wiki_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_skin_wiki_updated_at();

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE skin_wiki_articles IS 'Educational articles about skin cancer types, prevention, and self-examination';
COMMENT ON TABLE skin_wiki_versions IS 'Version history for tracking changes to Skin-Wiki articles';
COMMENT ON COLUMN skin_wiki_articles.version IS 'Current version number, incremented on each update';
COMMENT ON COLUMN skin_wiki_articles.published IS 'Whether article is visible to public users';
COMMENT ON COLUMN skin_wiki_versions.content IS 'Complete article content as JSONB snapshot';
