use crate::utils::vendor_detector::detect_vendor;
use regex::Regex;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Candidate {
    pub value: String,
    pub score: f32,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct ParseResult {
    pub base_url: Option<String>,
    pub api_key: Option<String>,
    pub vendor: String,
    pub url_candidates: Vec<Candidate>,
    pub key_candidates: Vec<Candidate>,
}

pub struct TextParser;

impl TextParser {
    pub fn parse(text: &str) -> ParseResult {
        let url_candidates = Self::find_url_candidates(text);
        let key_candidates = Self::find_key_candidates(text);

        let base_url = url_candidates.first().map(|c| c.value.clone());
        let api_key = key_candidates.first().map(|c| c.value.clone());

        let vendor = if let Some(ref url) = base_url {
            detect_vendor(url)
        } else {
            "custom".to_string()
        };

        ParseResult {
            base_url,
            api_key,
            vendor,
            url_candidates,
            key_candidates,
        }
    }

    fn find_url_candidates(text: &str) -> Vec<Candidate> {
        let re = Regex::new(r#"https?://[^\s,;。，；'"\]]+(?:/[^\s,;。，；'"\]]*)?"#).unwrap();
        let mut candidates = Vec::new();

        for mat in re.find_iter(text) {
            let mut url = mat.as_str().to_string();
            // Trim trailing punctuation
            url = url
                .trim_end_matches(|c: char| ".,;:!?。，；：！？".contains(c))
                .to_string();

            if !url.is_empty() {
                let score = Self::score_url(&url);
                candidates.push(Candidate { value: url, score });
            }
        }

        candidates.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());
        // Deduplicate
        let mut seen = std::collections::HashSet::new();
        candidates.retain(|c| seen.insert(c.value.clone()));

        candidates
    }

    fn find_key_candidates(text: &str) -> Vec<Candidate> {
        let mut candidates = Vec::new();

        // 1. OpenAI format sk-
        let sk_re = Regex::new(r"sk-[A-Za-z0-9]{20,}").unwrap();
        for mat in sk_re.find_iter(text) {
            candidates.push(Candidate {
                value: mat.as_str().to_string(),
                score: 0.95,
            });
        }

        // 2. Bearer Token
        let bearer_re = Regex::new(r"(?i)Bearer\s+([A-Za-z0-9_-]{20,})").unwrap();
        for cap in bearer_re.captures_iter(text) {
            if let Some(mat) = cap.get(1) {
                candidates.push(Candidate {
                    value: mat.as_str().to_string(),
                    score: 0.9,
                });
            }
        }

        // 3. Other long strings
        for line in text.lines() {
            let line = line.trim();
            if line.starts_with("http") {
                continue;
            }
            if line.chars().any(|c| ('\u{4e00}'..='\u{9fff}').contains(&c)) {
                continue;
            }

            if line.len() >= 32 && line.len() <= 100 {
                let long_str_re = Regex::new(r"^[A-Za-z0-9_-]+$").unwrap();
                if long_str_re.is_match(line) {
                    candidates.push(Candidate {
                        value: line.to_string(),
                        score: 0.7,
                    });
                }
            }
        }

        candidates.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());
        let mut seen = std::collections::HashSet::new();
        candidates.retain(|c| seen.insert(c.value.clone()));

        candidates
    }

    pub fn parse_model_names(text: &str) -> Vec<String> {
        let patterns = [
            r"(?i)gpt-[\w.-]+",
            r"(?i)claude-[\w.-]+",
            r"(?i)gemini-[\w.-]+",
            r"(?i)deepseek-[\w.-]+",
            r"(?i)glm-[\w.-]+",
            r"(?i)moonshot-[\w.-]+",
            r"[\w-]+-\d{8,}",
            r"(?i)o1-[\w.-]+",
            r"(?i)text-[\w.-]+",
        ];

        let mut models = std::collections::HashSet::new();

        for pattern in patterns {
            let re = Regex::new(pattern).unwrap();
            for mat in re.find_iter(text) {
                let model = mat.as_str().to_lowercase();
                if model.len() >= 3 && model.len() <= 80 {
                    models.insert(model);
                }
            }
        }

        let mut result: Vec<String> = models.into_iter().collect();
        result.sort();
        result
    }

    fn score_url(url: &str) -> f32 {
        let mut score: f32 = 0.4;
        let url_lower = url.to_lowercase();

        if url_lower.contains("/v1") {
            score += 0.3;
        }

        if url_lower.starts_with("https://") {
            score += 0.1;
        }

        let known_domains = [
            "openai.com",
            "anthropic.com",
            "googleapis.com",
            "deepseek",
            "zhipuai",
            "moonshot",
        ];
        if known_domains.iter().any(|&d| url_lower.contains(d)) {
            score += 0.2;
        }

        score.min(1.0)
    }
}
