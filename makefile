CXXFLAGS := $(shell llvm-config --cxxflags)
LLVMLDFLAGS := $(shell llvm-config --ldflags --libs)
SOURCES = src/uh.cpp \
    src/IncludeHandler.cpp
OBJECTS = $(SOURCES:.cpp=.o)
CLANGLIBS = -lclangRewrite \
    -lclangParse \
    -lclangSema \
    -lclangAnalysis \
    -lclangAST \
    -lclangDriver \
    -lclangSerialization \
	-lclangFrontend \
	-lclangLex \
	-lclangBasic \
	-lLLVMSupport \
	-lLLVMSystem \

uh: $(OBJECTS) 
	$(CXX) $(OBJECTS) $(CLANGLIBS) $(LLVMLDFLAGS) -o src/$@

%: %.o
	$(CXX) -o $@ $< $(CLANGLIBS) $(LLVMLDFLAGS)

clean:
	-rm -f $(EXES) $(OBJECTS) *~
