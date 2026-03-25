import { search } from './api';

describe('api', () => {
  vi.stubGlobal('fetch', vi.fn());

  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('search', () => {
    describe('Sad', () => {
      it('throws an error when fetch fails', async () => {
        vi.mocked(fetch).mockResolvedValue({ ok: false, status: 400 } as any);
        await expect(search('some query')).rejects.toThrow('400 when fetching');
      });
    });

    describe('Happy', () => {
      let result: any;

      beforeEach(async () => {
        vi.mocked(fetch).mockResolvedValue({
          ok: true,
          json: vi.fn().mockResolvedValue({ episodes: [{ foo: 'jazz' }] })
        } as any);

        result = await search('some query');
      });

      it('calls fetch', () => {
        const url = new URL(vi.mocked(fetch).mock.calls[0][0] as string);
        expect(fetch).toHaveBeenCalledTimes(1);
        expect(url.searchParams.get('q')).toBe('some query');
      });

      it('returns the data', () => {
        expect(result).toEqual([{ foo: 'jazz' }]);
      });
    });
  });
});
