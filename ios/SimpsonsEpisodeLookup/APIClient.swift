import Foundation

struct APIClient {
    static func search(query: String) async throws -> String {
        // Build GET /search?q={query} request against Config.apiBaseURL
        // Decode response and return formatted result string
    }
}
