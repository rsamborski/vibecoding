package com.example.news;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import java.time.LocalDateTime;
import java.util.Arrays;

@Component
public class DataLoader implements CommandLineRunner {

    private final NewsRepository newsRepository;

    public DataLoader(NewsRepository newsRepository) {
        this.newsRepository = newsRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        newsRepository.saveAll(Arrays.asList(
            new News(LocalDateTime.now().minusDays(1), "The first news item.", "John Doe"),
            new News(LocalDateTime.now().minusDays(2), "This is the second news item.", "Jane Smith"),
            new News(LocalDateTime.now().minusDays(3), "A third news item has appeared.", "Peter Jones"),
            new News(LocalDateTime.now().minusDays(4), "Fourth news item, fresh off the press.", "Mary Williams"),
            new News(LocalDateTime.now().minusDays(5), "News item number five.", "David Brown"),
            new News(LocalDateTime.now().minusDays(6), "This is the sixth news item.", "Susan Miller"),
            new News(LocalDateTime.now().minusDays(7), "Seventh news item for your viewing pleasure.", "Robert Davis"),
            new News(LocalDateTime.now().minusDays(8), "The eighth news item is here.", "Linda Garcia"),
            new News(LocalDateTime.now().minusDays(9), "Ninth news item, hot off the wire.", "Michael Rodriguez"),
            new News(LocalDateTime.now().minusDays(10), "Tenth news item, read all about it.", "Elizabeth Martinez"),
            new News(LocalDateTime.now().minusDays(11), "Eleventh news item, just in.", "William Hernandez"),
            new News(LocalDateTime.now().minusDays(12), "Twelfth news item, a must-read.", "Karen Lopez"),
            new News(LocalDateTime.now().minusDays(13), "The thirteenth news item has arrived.", "Charles Gonzalez"),
            new News(LocalDateTime.now().minusDays(14), "Fourteenth news item, don't miss it.", "Anthony Wilson"),
            new News(LocalDateTime.now().minusDays(15), "Fifteenth and final news item for now.", "Patricia Anderson")
        ));
    }
}
