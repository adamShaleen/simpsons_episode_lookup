import Observation

@Observable
final class EpisodeViewModel {
    var query: String = ""
    var result: String = ""
    var isLoading: Bool = false
    var errorMessage: String? = nil

    func search() async {
        // Call APIClient.search(query:), update result or errorMessage
    }
}
