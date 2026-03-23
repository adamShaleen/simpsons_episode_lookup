import SwiftUI

struct ContentView: View {
    @State private var viewModel = EpisodeViewModel()

    var body: some View {
        // Search field bound to viewModel.query
        // Search button that calls viewModel.search()
        // Loading indicator when viewModel.isLoading
        // Result text when viewModel.result is non-empty
        // Error text when viewModel.errorMessage is non-nil
    }
}
